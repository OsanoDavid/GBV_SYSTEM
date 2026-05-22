import os
import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from dotenv import load_dotenv

from .models import IncidentReport
from .forms import SecureIncidentReportForm

# -------------------------------------------------------------
# CORE CONFIGURATION: ENVIRONMENT LOADERS
# -------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# -------------------------------------------------------------
# INCIDENT REPORT MANIFEST LAYERS
# -------------------------------------------------------------
def landing_view(request):
    """Renders the primary platform landing welcome hub."""
    return render(request, 'core/landing.html')


def file_report_view(request):
    """Handles secure submission of guest or logged-in user incident report profiles."""
    if request.method == 'POST':
        form = SecureIncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            if request.user.is_authenticated:
                incident.reporter_profile = request.user
            incident.save()
            return redirect('report_success', ref_num=incident.reference_number)
    else:
        form = SecureIncidentReportForm()
    return render(request, 'reports/file_report.html', {'form': form})


def report_success_view(request, ref_num):
    """Outputs the secure reference confirmation key payload upon database write entry."""
    return render(request, 'reports/report_success.html', {'ref_num': ref_num})


def track_case_view(request):
    """Provides unauthenticated token matching search capabilities."""
    query = request.GET.get('query', '').strip()
    report = None
    searched = False
    
    if query:
        searched = True
        report = IncidentReport.objects.filter(reference_number=query).first()
        
    return render(request, 'reports/track_case.html', {
        'report': report, 
        'query': query, 
        'searched': searched
    })


# -------------------------------------------------------------
# AUTHENTICATION HUB CONTROL PLATFORMS
# -------------------------------------------------------------
def register_user_view(request):
    """Handles secure onboarding for users wishing to create a dashboard account."""
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
    """Compiles and renders cases explicitly linked to the logged-in individual profile."""
    user_reports = IncidentReport.objects.filter(reporter_profile=request.user).order_by('-created_at')
    return render(request, 'reports/dashboard.html', {'reports': user_reports})


# -------------------------------------------------------------
# DYNAMIC CONVERSATIONAL BRAIN ENGINES (OFFICIAL SDK)
# -------------------------------------------------------------
def ai_assistant_chat_view(request):
    """
    Processes real-time conversation prompts using the modern Google GenAI SDK client architecture,
    explicitly targeting the project's supported Gemini 3 platform backend.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'status': 'success', 'reply': "Please type something so I can support you."})

            if not GEMINI_API_KEY:
                return JsonResponse({
                    'status': 'success',
                    'reply': "System note: API Key configuration missing from .env file."
                })

            # Import the modern Google GenAI SDK
            from google import genai
            from google.genai import types

            # Initialize the modern client
            client = genai.Client(api_key=GEMINI_API_KEY)

            system_instruction = (
                "You are a compassionate, highly empathetic human counselor and safety advocate working "
                "for 'SafeSpace', a secure platform designed to support survivors of online harassment and "
                "technology-facilitated gender-based violence (TFGBV).\n\n"
                "Your objective is to converse like an authentic, supportive, grounded human professional—not "
                "a rigid corporate computer program. Acknowledge and validate the user's feelings with deep empathy. "
                "Keep your sentences conversational, clear, free of robotic technical jargon, and concise.\n\n"
                "If users describe immediate danger, gently encourage them to contact emergency services or use "
                "the 'Quick Escape' button. If they ask about saving files, tell them to securely keep uncropped screenshots "
                "with visible timestamps, URLs, and communication paths."
            )

            # FIX: Swapped out 'gemini-1.5-flash' for the active 'gemini-3-flash-preview' identifier
           # OPTION A: The fully qualified preview identifier
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Or try 'gemini-2.0-flash' / 'gemini-3.0-flash-preview'
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                ),
            )
            
            ai_reply = response.text.strip()
            return JsonResponse({'status': 'success', 'reply': ai_reply})

        except Exception as e:
            print(f"\n[Modern GenAI Client Error]: {str(e)}\n")
            return JsonResponse({
                'status': 'error', 
                'reply': "I'm right here with you, but I encountered a quick connection stutter. Could you resend that message?"
            }, status=200)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)