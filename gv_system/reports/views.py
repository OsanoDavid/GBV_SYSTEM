import os
import json
import random
import string
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import F
from django.db.models.functions import ACos, Cos, Sin, Radians
from dotenv import load_dotenv

from .models import IncidentReport, ChildrensHome
from .forms import SecureIncidentReportForm
from reports.services import AssignmentService

# -------------------------------------------------------------
# CORE CONFIGURATION: ENVIRONMENT LOADERS
# -------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ICON_MAP = {
    'cyberstalking': 'icons/eye-slash.html',
    'doxing': 'icons/shield-exclamation.html',
    'impersonation': 'icons/user.html',
    'threats': 'icons/exclamation-triangle.html',
}

# -------------------------------------------------------------
# INCIDENT REPORT MANIFEST LAYERS
# -------------------------------------------------------------
def landing_view(request):
    return render(request, 'core/landing.html', {'icon_map': ICON_MAP})

def file_report_view(request):
    if request.method == 'POST':
        form = SecureIncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            
            # --- MANDATORY CODE GENERATION ---
            part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            incident.reference_number = f"GBV-{part1}-{part2}"
            incident.case_access_pin = ''.join(random.choices(string.digits, k=6))
            
            if request.user.is_authenticated:
                incident.reporter_profile = request.user
            
            incident.save()
            
            # --- AUTOMATIC ROUTING ---
            AssignmentService.auto_route_report(incident.id)
            
            return render(request, 'reports/report_success.html', {
                'reference': incident.reference_number, 
                'pin': incident.case_access_pin
            })
    else:
        form = SecureIncidentReportForm()
    return render(request, 'reports/file_report.html', {'form': form})

def report_success_view(request, ref_num):
    # Fallback if accessed directly
    return render(request, 'reports/report_success.html', {'ref_num': ref_num})

def track_case_view(request):
    report = None
    if request.method == "POST":
        ref_num = request.POST.get('reference_number', '').strip()
        pin = request.POST.get('case_access_pin', '').strip()
        if ref_num and pin:
            try:
                report = IncidentReport.objects.get(
                    reference_number__iexact=ref_num, 
                    case_access_pin=pin
                )
            except IncidentReport.DoesNotExist:
                report = None 
    return render(request, 'reports/track_case.html', {'report': report})

# -------------------------------------------------------------
# LOCATION-BASED ASSISTANCE ENGINE
# -------------------------------------------------------------
def find_homes_view(request):
    try:
        user_lat = float(request.GET.get('lat', 0))
        user_lon = float(request.GET.get('lon', 0))
        homes = ChildrensHome.objects.annotate(
            distance=(
                6371 * ACos(
                    Cos(Radians(user_lat)) * Cos(Radians(F('latitude'))) *
                    Cos(Radians(F('longitude')) - Radians(user_lon)) +
                    Sin(Radians(user_lat)) * Sin(Radians(F('latitude')))
                )
            )
        ).order_by('distance')[:3]
        return render(request, 'reports/nearby_results.html', {'homes': homes})
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid coordinates.'}, status=400)

# -------------------------------------------------------------
# AUTHENTICATION & DASHBOARD
# -------------------------------------------------------------
def register_user_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_dashboard_view(request):
    user_reports = IncidentReport.objects.filter(reporter_profile=request.user).order_by('-created_at')
    return render(request, 'reports/dashboard.html', {'reports': user_reports})

# -------------------------------------------------------------
# DYNAMIC CONVERSATIONAL BRAIN ENGINES
# -------------------------------------------------------------
def ai_assistant_chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            if not user_message:
                return JsonResponse({'status': 'success', 'reply': "Please type something."})
            if not GEMINI_API_KEY:
                return JsonResponse({'status': 'success', 'reply': "System note: API Key missing."})

            from google import genai
            from google.genai import types
            client = genai.Client(api_key=GEMINI_API_KEY)
            system_instruction = "You are a compassionate human counselor for 'SafeSpace' supporting survivors. Be empathetic."
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7),
            )
            return JsonResponse({'status': 'success', 'reply': response.text.strip()})
        except Exception as e:
            return JsonResponse({'status': 'error', 'reply': "Connection issue, please resend."}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)