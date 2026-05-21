from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import IncidentReport
from .forms import SecureIncidentReportForm

def landing_view(request):
    """Renders the primary platform landing welcome hub."""
    return render(request, 'core/landing.html')

def file_report_view(request):
    """Handles secure submission of guest or logged-in user incident report profiles."""
    if request.method == 'POST':
        form = SecureIncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            # If a user is securely logged in, link this case automatically
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

# --- PHASE 5 AUTHENTICATION VIEWS ADDED HERE ---

def register_user_view(request):
    """Handles secure onboarding for users wishing to create a dashboard account."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically logs the user in after registration
            return redirect('user_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_dashboard_view(request):
    """Compiles and renders cases explicitly linked to the logged-in individual profile."""
    user_reports = IncidentReport.objects.filter(reporter_profile=request.user).order_by('-created_at')
    return render(request, 'reports/dashboard.html', {'reports': user_reports})