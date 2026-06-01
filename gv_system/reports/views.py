import os, json, random, string, logging
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import F, Q
from django.db.models.functions import ACos, Cos, Sin, Radians
from dotenv import load_dotenv

from .models import Department, IncidentReport, ChildrensHome, AuditLog
from .forms import SecureIncidentReportForm
from reports.notifications import send_tracking_sms
from reports.services import AssignmentService

load_dotenv()
logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")

def is_staff(user):
    return user.is_staff or user.groups.filter(name='DepartmentStaff').exists()

# -------------------------------------------------------------
# CORE VIEWS
# -------------------------------------------------------------
def landing_view(request):
    return render(request, 'core/landing.html')

def file_report_view(request):
    if request.method == 'POST':
        form = SecureIncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                incident = form.save(commit=False)

                # Handle custom category if "other" was selected
                if incident.incident_category == 'other':
                    custom_cat = form.cleaned_data.get('custom_category', '').strip()
                    if custom_cat:
                        incident.incident_category = custom_cat
                    else:
                        # If no custom category provided, reject the form
                        messages.error(request, "Please specify a custom incident type when selecting 'Other'.")
                        return render(request, 'reports/file_report.html', {'form': form})

                # 1. Generate new values
                ref = f"GBV-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
                pin = ''.join(random.choices(string.digits, k=6))

                # 2. Assign to instance
                incident.reference_number = ref
                incident.case_access_pin = pin

                if request.user.is_authenticated:
                    incident.reporter_profile = request.user

                incident.save()

                # 3. DEBUG PRINT: Look at your terminal!
                logger.info("Saved Report ID %s | Ref: %s | PIN: %s", incident.id, incident.reference_number, incident.case_access_pin)

                user_lat = request.POST.get('user_lat') or request.session.get('last_user_lat')
                user_lng = request.POST.get('user_lng') or request.session.get('last_user_lng')
                nearest_home_id = request.session.get('last_nearest_home_id')
                
                try:
                    AssignmentService.auto_route_report(
                        incident.id,
                        user=request.user if request.user.is_authenticated else None,
                        user_lat=user_lat,
                        user_lng=user_lng,
                        nearest_home_id=nearest_home_id,
                    )
                except Exception as e:
                    logger.warning("Assignment service failed: %s", str(e))
                    AuditLog.objects.create(
                        report=incident,
                        user=request.user if request.user.is_authenticated else None,
                        action=f"Assignment service error: {str(e)}"
                    )
                
                try:
                    sms_sent, sms_status = send_tracking_sms(incident)
                    AuditLog.objects.create(
                        report=incident,
                        user=request.user if request.user.is_authenticated else None,
                        action=sms_status
                    )
                except Exception as e:
                    logger.warning("SMS sending failed: %s", str(e))
                    AuditLog.objects.create(
                        report=incident,
                        user=request.user if request.user.is_authenticated else None,
                        action=f"SMS error: {str(e)}"
                    )

                # 4. Explicit Context
                return render(request, 'reports/report_success.html', {
                    'reference': incident.reference_number,
                    'pin': incident.case_access_pin
                })
            except Exception as e:
                # Log full traceback and show a friendly message
                logger.exception("Unhandled exception while processing report submission")
                messages.error(request, "We encountered an error processing your report. Please try again later or contact support.")
                # Fall through to re-render the form with the filled data
        else:
            # Form validation failed - log the errors
            logger.warning("Form validation failed: %s", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SecureIncidentReportForm()
    return render(request, 'reports/file_report.html', {'form': form})

def track_case_view(request):
    report = None
    if request.method == "POST":
        ref = request.POST.get('reference_number', '').strip()
        pin = request.POST.get('case_access_pin', '').strip()
        if ref and pin:
            report = IncidentReport.objects.filter(reference_number__iexact=ref, case_access_pin=pin).first()
            if report:
                refresh_report_workflow(report, request)
    return render(request, 'reports/track_case.html', {'report': report})

# -------------------------------------------------------------
# ADMIN & STAFF
# -------------------------------------------------------------
@staff_member_required
def custom_admin_dashboard(request):
    return render(request, 'reports/custom_admin_dashboard.html', {
        'total_reports': IncidentReport.objects.count(),
        'recent_reports': IncidentReport.objects.all().order_by('-created_at'),
        'recent_logs': AuditLog.objects.all().order_by('-timestamp')[:15],
    })

@staff_member_required
def friendly_edit_view(request, report_id):
    report = get_object_or_404(IncidentReport, id=report_id)
    if request.method == 'POST':
        form = SecureIncidentReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.admin_notes = request.POST.get('admin_notes', '')
            report.status = request.POST.get('status', report.status)
            report.level = request.POST.get('level', report.level)
            report.assigned_department_id = request.POST.get('assigned_department') or None
            report.assigned_home_id = request.POST.get('assigned_home') or None
            report.save()
            AuditLog.objects.create(
                report=report,
                user=request.user,
                action="Admin updated full case record from command center."
            )
            return redirect('custom_admin_dashboard')
    else:
        form = SecureIncidentReportForm(instance=report)
    return render(request, 'reports/friendly_edit.html', {
        'form': form,
        'report': report,
        'departments': Department.objects.all().order_by('name'),
        'homes': ChildrensHome.objects.all().order_by('name'),
    })

@staff_member_required
def delete_report_view(request, report_id):
    get_object_or_404(IncidentReport, id=report_id).delete()
    return redirect('custom_admin_dashboard')

@staff_member_required
def send_case_sms_view(request, report_id):
    report = get_object_or_404(IncidentReport, id=report_id)
    sms_sent, sms_status = send_tracking_sms(report)
    AuditLog.objects.create(report=report, user=request.user, action=sms_status)
    return redirect('friendly_edit', report_id=report.id)

# -------------------------------------------------------------
# UTILITIES
# -------------------------------------------------------------
def refresh_report_workflow(report, request=None):
    if (
        request
        and report.incident_category == 'children_home_support'
        and not report.assigned_home_id
    ):
        home = AssignmentService.find_nearest_home(
            request.session.get('last_user_lat'),
            request.session.get('last_user_lng'),
            request.session.get('last_nearest_home_id'),
        )
        if home:
            report.assigned_home = home
            report.save(update_fields=['assigned_home', 'updated_at'])
            AuditLog.objects.create(
                report=report,
                user=None,
                action=f"Nearest children's home automatically assigned: {home.name}."
            )

    if report.status == 'pending' and (report.assigned_department_id or report.assigned_home_id):
        report.status = 'under_review'
        report.save(update_fields=['status', 'updated_at'])
        AuditLog.objects.create(
            report=report,
            user=None,
            action="Status automatically updated after routing assignment."
        )

def find_homes_view(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng') or request.GET.get('lon')

    try:
        user_lat = float(lat)
        user_lng = float(lng)
    except (TypeError, ValueError):
        return render(request, 'reports/nearby_results.html', {
            'homes': [],
            'error_message': 'We could not read your location. Please allow location access and try again.'
        })

    homes = AssignmentService.get_nearby_homes(user_lat, user_lng)
    request.session['last_user_lat'] = user_lat
    request.session['last_user_lng'] = user_lng
    request.session['last_nearest_home_id'] = homes[0].id if homes else None
    return render(request, 'reports/nearby_results.html', {
        'homes': homes[:5],
        'user_lat': user_lat,
        'user_lng': user_lng,
    })

def ai_assistant_chat_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=405)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'reply': 'I am here. Type your question or tell me what happened, and I will guide you.'})

    if not GEMINI_API_KEY:
        return JsonResponse({
            'status': 'error',
            'reply': 'The AI assistant is not configured yet. Please add GEMINI_API_KEY to your environment.'
        }, status=200)

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are SafeSpace Support Bot, a calm and compassionate assistant for a "
                    "technology-facilitated gender-based violence reporting platform. Give short, "
                    "practical, trauma-informed answers. Help users file reports, track cases, "
                    "preserve evidence, and find emergency resources. If the user may be in "
                    "immediate danger, tell them to contact emergency services and mention Kenya "
                    "helplines 999, 116, and 1195. Do not claim to be a lawyer, doctor, or police officer."
                )
            }]
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": user_message}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000
        }
    }

    try:
        response = requests.post(
            endpoint,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        candidates = result.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            reply = "".join(part.get("text", "") for part in parts).strip()
        else:
            reply = "I am sorry, but I cannot provide a response to that. How else can I help you?"
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        reply = (
            f"I encountered an error connecting to the AI: {str(e)}. "
            "You can still file a report, track a case, or save evidence such as "
            "screenshots, usernames, links, dates, and message records."
        )

    return JsonResponse({'status': 'success', 'reply': reply or 'I am here. Please try asking that another way.'})

def register_user_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Grant staff status so users can access admin panel
            user.is_staff = True
            user.save()
            messages.success(request, f"Registration successful for {user.username}. You can now log in and access your dashboard.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
@login_required
def user_dashboard_view(request):
    query = Q(reporter_profile=request.user)
    if request.user.email:
        query |= Q(reporter_email__iexact=request.user.email)
    reports = IncidentReport.objects.filter(query).order_by('-created_at')
    return render(request, 'reports/dashboard.html', {'reports': reports})

def report_success_view(request):
    """Placeholder to stop the ImportError; logic is handled in file_report_view."""
    return render(request, 'reports/report_success.html')
@login_required
@user_passes_test(is_staff)
def department_portal_view(request):
    """View to show reports assigned to the logged-in staff member's department."""
    reports = IncidentReport.objects.filter(assigned_department__email=request.user.email)
    return render(request, 'reports/department_portal.html', {'reports': reports})
@login_required
def update_case_status(request, report_id):
    from .models import IncidentReport, AuditLog
    report = get_object_or_404(IncidentReport, pk=report_id)
    if request.method == "POST":
        new_status = request.POST.get('status')
        report.status = new_status
        report.save()
        AuditLog.objects.create(
            report=report, user=request.user, 
            action=f"Department updated status to {new_status}"
        )
        return redirect('department_portal')
    return render(request, 'reports/update_status.html', {'report': report})
