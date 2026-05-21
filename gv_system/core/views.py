from django.shortcuts import render

def landing_page_view(request):
    """Render the responsive deep purple primary landing page."""
    return render(request, 'core/landing.html')