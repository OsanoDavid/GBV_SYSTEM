from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, ChildrensHome, Department, IncidentReport, AdminProfile
from .utils import check_email_connection


admin.site.site_header = "SafeSpace Command Center"
admin.site.index_title = f"Reports | System Status: {'SMTP Connected' if check_email_connection() else 'SMTP Error'}"


class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0
    readonly_fields = ('user', 'action', 'timestamp')
    can_delete = False


class AssignedIncidentInline(admin.TabularInline):
    model = IncidentReport
    extra = 0
    fields = ('reference_number', 'incident_category', 'status', 'assigned_home', 'created_at')
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class ChildrensHomeIncidentInline(admin.TabularInline):
    model = IncidentReport
    fk_name = 'assigned_home'
    extra = 0
    fields = ('reference_number', 'incident_category', 'status', 'assigned_department', 'created_at')
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(IncidentReport)
class SecureIncidentReportAdmin(admin.ModelAdmin):
    list_display = (
        'reference_number',
        'case_access_pin',
        'reporter_phone',
        'incident_category',
        'status',
        'assigned_department',
        'assigned_home',
        'created_at',
        'level',
    )
    list_filter = ('status', 'ai_urgency_score', 'incident_category', 'created_at', 'assigned_department', 'assigned_home', 'level')
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
    actions = ['mark_as_urgent', 'resolve_case', 'close_case']
    inlines = [AuditLogInline]

    def has_delete_permission(self, request, obj=None):
        return False

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

    @admin.action(description="Close Case")
    def close_case(self, request, queryset):
        rows_updated = queryset.update(status='closed')
        for report in queryset:
            AuditLog.objects.create(report=report, user=request.user, action="Admin closed case.")
        self.message_user(request, f"{rows_updated} reports were marked as Closed.")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'assigned_cases')
    search_fields = ('name', 'email')
    inlines = [AssignedIncidentInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(assigned_case_count=Count('incidentreport'))

    @admin.display(description='Assigned cases', ordering='assigned_case_count')
    def assigned_cases(self, obj):
        return obj.assigned_case_count


@admin.register(ChildrensHome)
class ChildrensHomeAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'assigned_cases', 'lat', 'lng', 'address')
    search_fields = ('name', 'phone', 'address')
    inlines = [ChildrensHomeIncidentInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(assigned_case_count=Count('incidentreport'))

    @admin.display(description='Assigned cases', ordering='assigned_case_count')
    def assigned_cases(self, obj):
        return obj.assigned_case_count


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('report', 'action', 'user', 'timestamp')
    readonly_fields = ('timestamp',)


# --- MULTI-ADMIN MANAGEMENT ---

class AdminProfileInline(admin.StackedInline):
    """Inline for managing AdminProfile within User admin"""
    model = AdminProfile
    extra = 0
    fields = ('admin_level', 'manages_departments', 'is_active', 'notes')


class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with AdminProfile management"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'admin_level_display')
    list_filter = BaseUserAdmin.list_filter + ('admin_profile__admin_level', 'admin_profile__is_active')
    inlines = [AdminProfileInline]

    def admin_level_display(self, obj):
        """Display admin level if user has AdminProfile"""
        try:
            return obj.admin_profile.get_admin_level_display()
        except AdminProfile.DoesNotExist:
            return "Not an Admin"
    admin_level_display.short_description = "Admin Level"


# Unregister the default UserAdmin and use the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_level', 'is_active', 'department_count', 'created_at')
    list_filter = ('admin_level', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'notes')
    filter_horizontal = ('manages_departments',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active')
        }),
        ('Admin Role & Permissions', {
            'fields': ('admin_level', 'manages_departments')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at', 'updated_at'),
        }),
    )

    def department_count(self, obj):
        """Show number of departments managed"""
        return obj.manages_departments.count()
    department_count.short_description = "Departments Managed"
