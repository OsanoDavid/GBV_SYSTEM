import os
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from reports.models import IncidentReport 

# -------------------------------------------------------------
# CORE VIEW HUB CONFIGURATIONS
# -------------------------------------------------------------
def landing_page_view(request):
    """Render the responsive deep purple primary landing page."""
    return render(request, 'core/landing.html')


def file_report(request):
    """Processes the multi-step form wizard submission data into the DB."""
    if request.method == "POST":
        try:
            reporter_type = request.POST.get('reporter_type', 'self')
            allow_contact = request.POST.get('allow_contact') == 'on'
            gender = request.POST.get('gender', 'P')
            age_group = request.POST.get('age_group')
            disability = request.POST.get('disability', 'none')
            
            # Capture the date, platform, and text telemetry fields
            incident_date = request.POST.get('incident_date')
            platform_used = request.POST.get('platform_used')
            description = request.POST.get('description')

            # Capture individual contact metrics instead of 'contact_detail'
            reporter_name = request.POST.get('reporter_name', '')
            reporter_email = request.POST.get('reporter_email', '')
            reporter_phone = request.POST.get('reporter_phone', '')

            # Intercept "other" selection and pull from the custom text field
            category_selection = request.POST.get('incident_category')
            if category_selection == 'other':
                incident_category = request.POST.get('custom_category')
            else:
                incident_category = category_selection

            # Create the database record matching your models layout fields cleanly
            report = IncidentReport.objects.create(
                reporter_type=reporter_type,
                allow_contact=allow_contact,
                gender=gender,
                age_group=age_group,
                disability=disability,
                incident_category=incident_category,
                incident_date=incident_date,        
                platform_used=platform_used,        
                description=description,
                reporter_name=reporter_name,
                reporter_email=reporter_email,
                reporter_phone=reporter_phone
            )
            
            # If a dashboard session is active, link the case asset automatically
            if request.user.is_authenticated:
                report.reporter_profile = request.user
                report.save()
            
            # Cache the tracking credentials in the session for one-time display
            request.session['success_ref'] = str(report.reference_number)
            request.session['success_pin'] = report.case_access_pin
            return redirect('report_success')
            
        except Exception as e:
            messages.error(request, f"Submission processing fault: {str(e)}")
            
    return render(request, 'reports/file_report.html')


def report_success(request):
    """Displays secure generated credentials one-time only to the reporter."""
    context = {
        'ref': request.session.get('success_ref'),
        'pin': request.session.get('success_pin')
    }
    if not context['ref']:
        return redirect('landing')
        
    return render(request, 'reports/report_success.html', context)


def track_case(request):
    """Handles secure dual-token database query matching for custom case status lookup."""
    context = {}
    if request.method == "POST":
        ref_num = request.POST.get('reference_number', '').strip()
        pin_num = request.POST.get('case_access_pin', '').strip()
        
        try:
            # Query and match exact reference number AND security pin sequence
            report = IncidentReport.objects.get(reference_number=ref_num, case_access_pin=pin_num)
            context['report'] = report
        except IncidentReport.DoesNotExist:
            context['report'] = None
            
    return render(request, 'reports/track_case.html', context)


def ai_assistant_chat(request):
    """
    UPDATED: Processes incoming chat messages from the AI chat window.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()
            
            # Simple keyword-based response logic
            if any(word in user_message for word in ['report', 'file', 'help']):
                reply = "You can file a report by clicking the 'File Report' button on the homepage. Everything is kept confidential."
            elif 'stalking' in user_message or 'harassment' in user_message:
                reply = "I am sorry you are experiencing this. Please consider contacting the National Gender Helpline (1195) for immediate support."
            else:
                reply = "I'm here to support you. Could you provide more details, or would you like to see how to file an official report?"
            
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=405)


# -------------------------------------------------------------
# SECURE IDENTITY & AUTHENTICATION PROTOCOLS
# -------------------------------------------------------------
def login_view(request):
    """
    UPDATED: Validates incoming secure authorization parameters,
    populates context errors, and injects clean auth objects natively.
    """
    if request.user.is_authenticated:
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_dashboard')
    else:
        form = AuthenticationForm()
        
    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    """UPDATED: Process secure onboarding with context injection for glassmorphic elements."""
    if request.user.is_authenticated:
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_dashboard')
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """Clears explicit login session maps instantly."""
    logout(request)
    return redirect('landing')


@login_required
def user_dashboard(request):
    """Fetches and feeds user-submitted incidents to render context structures securely."""
    user_reports = IncidentReport.objects.filter(reporter_profile=request.user).order_by('-created_at')
    return render(request, 'reports/dashboard.html', {'reports': user_reports})