from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import IncidentReport

@admin.register(IncidentReport)
class SecureIncidentReportAdmin(admin.ModelAdmin):
    # Controls the columns displayed in the administrative list view
    list_display = ('reference_number', 'category', 'status', 'ai_urgency_score', 'created_at')
    
    # Injects interactive search and filter sidebars to handle large dataset triage
    list_filter = ('status', 'ai_urgency_score', 'category', 'created_at')
    search_fields = ('reference_number', 'description', 'reporter_name', 'reporter_email')
    
    # Organizes individual report inspection screens into clean information blocks
    fieldsets = (
        ('Case Tracking Identification', {
            'fields': ('reference_number', 'status', 'admin_notes')
        }),
        ('Incident Information Details', {
            'fields': ('category', 'description', 'incident_date', 'platform_used', 'evidence_attachment')
        }),
        ('Reporter Identity Metrics (Optional)', {
            'fields': ('reporter_profile', 'reporter_name', 'reporter_email', 'reporter_phone')
        }),
        ('Automated AI Analytics Cache Layer', {
            'fields': ('ai_classified_category', 'ai_urgency_score', 'ai_research_insights'),
            'classes': ('collapse',), # Keeps AI insights collapsable for visual cleanliness
        }),
    )
    
    # Prevents accidental security modification of system-generated metrics
    readonly_fields = ('reference_number', 'ai_classified_category', 'ai_urgency_score', 'ai_research_insights', 'created_at', 'updated_at')

    # Enforces absolute date chronological listing
    ordering = ('-created_at',)