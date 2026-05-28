from django.contrib import admin
from .models import IncidentReport, Department, ChildrensHome, AuditLog
from .utils import check_email_connection

# --- Configuration ---
admin.site.site_header = "SafeSpace Command Center"
admin.site.index_title = f"System Status: {'✅ SMTP Connected' if check_email_connection() else '❌ SMTP Error'}"

# --- Inlines ---
class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0
    readonly_fields = ('user', 'action', 'timestamp')
    can_delete = False

# --- Admin Registrations ---
@admin.register(IncidentReport)
class SecureIncidentReportAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'case_access_pin', 'reporter_phone', 'incident_category', 'status', 'assigned_home', 'created_at', 'level')
    list_filter = ('status', 'ai_urgency_score', 'incident_category', 'created_at', 'assigned_department', 'level')
    search_fields = ('reference_number', 'case_access_pin', 'incident_category', 'description', 'reporter_name', 'reporter_email', 'reporter_phone')
    
    fieldsets = (
        ('Case Tracking Identification', {
            'fields': ('reference_number', 'case_access_pin', 'status', 'admin_notes', 'assigned_department', 'assigned_home', 'assigned_to', 'level')
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
        ('System Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('Automated AI Analytics Cache Layer', {
            'fields': ('ai_classified_category', 'ai_urgency_score', 'ai_research_insights'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('reference_number', 'case_access_pin', 'ai_classified_category', 'ai_urgency_score', 'ai_research_insights', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    actions = ['mark_as_urgent', 'resolve_case']
    inlines = [AuditLogInline]

    @admin.action(description="Escalate to Urgent/Level 2")
    def mark_as_urgent(self, request, queryset):
        rows_updated = queryset.update(level=2)
        for report in queryset:
            AuditLog.objects.create(report=report, user=request.user, action="Admin escalated case to Level 2.")
        self.message_user(request, f"{rows_updated} reports were escalated to Urgent.")

    @admin.action(description="Resolve Case")
    def resolve_case(self, request, queryset):
        rows_updated = queryset.update(level=3, status='action_taken')
        for report in queryset:
            AuditLog.objects.create(report=report, user=request.user, action="Admin resolved case.")
        self.message_user(request, f"{rows_updated} reports were marked as Resolved.")

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

@admin.register(ChildrensHome)
class ChildrensHomeAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'lat', 'lng', 'address')
    search_fields = ('name', 'phone')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('report', 'action', 'user', 'timestamp')
    readonly_fields = ('timestamp',)
