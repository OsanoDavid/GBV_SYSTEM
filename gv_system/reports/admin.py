from django.contrib import admin
from .models import IncidentReport, Department, ChildrensHome, AuditLog

@admin.register(IncidentReport)
class SecureIncidentReportAdmin(admin.ModelAdmin):
    # Controls the columns displayed in the administrative list view
    list_display = ('reference_number', 'incident_category', 'status', 'ai_urgency_score', 'created_at', 'assigned_department')
    
    # Injects interactive search and filter sidebars
    list_filter = ('status', 'ai_urgency_score', 'incident_category', 'created_at', 'assigned_department')
    search_fields = ('reference_number', 'incident_category', 'description', 'reporter_name', 'reporter_email')
    
    # Organizes individual report inspection screens
    fieldsets = (
        ('Case Tracking Identification', {
            'fields': ('reference_number', 'case_access_pin', 'status', 'admin_notes', 'assigned_department', 'assigned_to', 'level')
        }),
        ('Incident Information Details', {
            'fields': ('incident_category', 'description', 'incident_date', 'platform_used', 'evidence_attachment')
        }),
        ('Demographics & Anonymity Settings', {
            'fields': ('reporter_type', 'gender', 'age_group', 'disability', 'allow_contact')
        }),
        ('Reporter Identity Metrics (Optional)', {
            'fields': ('reporter_profile', 'reporter_name', 'reporter_email', 'reporter_phone')
        }),
        ('Automated AI Analytics Cache Layer', {
            'fields': ('ai_classified_category', 'ai_urgency_score', 'ai_research_insights'),
            'classes': ('collapse',),
        }),
    )
    
    # Prevents accidental security modification
    readonly_fields = ('reference_number', 'case_access_pin', 'ai_classified_category', 'ai_urgency_score', 'ai_research_insights', 'created_at', 'updated_at')

    # Enforces absolute date chronological listing
    ordering = ('-created_at',)

# Registering the new Infrastructure models
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

@admin.register(ChildrensHome)
class ChildrensHomeAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'address')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('report', 'action', 'user', 'timestamp')
    readonly_fields = ('timestamp',)