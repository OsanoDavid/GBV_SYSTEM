import random
import string
from django.db import models
from django.contrib.auth.models import User

# --- Infrastructure ---
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField()

    def __str__(self):
        return self.name

class ChildrensHome(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"{self.name} ({self.phone})"

# --- Incident Management ---
class IncidentReport(models.Model):
    CATEGORY_CHOICES = [
        ('cyberstalking', 'Cyberstalking & Harassment'),
        ('doxing', 'Non-Consensual Image Sharing / DoXing'),
        ('impersonation', 'Impersonation & Identity Theft'),
        ('threats', 'Online Threats & Hate Speech'),
        ('other', 'Other Forms of Online Abuse'),
        ('children_home_support', 'Children\'s Home Support'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Investigation'),
        ('action_taken', 'Action Taken / Resolved'),
        ('closed', 'Closed'),
    ]

    URGENCY_CHOICES = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical Intervention Required'),
    ]

    LEVEL_CHOICES = [
        (0, 'Unassigned'),
        (1, 'Initial Review'),
        (2, 'Escalated/Urgent'),
        (3, 'Resolved')
    ]

    # --- Core Tracking ---
    reference_number = models.CharField(max_length=14, unique=True, editable=False, db_index=True)
    case_access_pin = models.CharField(max_length=6, editable=False)
    reporter_profile = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    # --- Incident Telemetry ---
    incident_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField()
    incident_date = models.DateField(null=True, blank=True)
    platform_used = models.CharField(max_length=100)
    evidence_attachment = models.FileField(upload_to='evidence/%Y/%m/%d/', blank=True, null=True)
    
    # --- Workflow & Assignment ---
    level = models.IntegerField(choices=LEVEL_CHOICES, default=0)
    assigned_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    # Integration of Children's Home logic
    assigned_home = models.ForeignKey(ChildrensHome, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- Metadata ---
    reporter_type = models.CharField(max_length=20, default='self')
    allow_contact = models.BooleanField(default=False)
    gender = models.CharField(max_length=5, default='P')
    age_group = models.CharField(max_length=10, blank=True, null=True)
    disability = models.CharField(max_length=20, default='none')
    reporter_name = models.CharField(max_length=100, blank=True, null=True)
    reporter_email = models.EmailField(blank=True, null=True)
    reporter_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # --- AI Metadata & Admin ---
    ai_classified_category = models.CharField(max_length=50, blank=True, null=True)
    ai_urgency_score = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='low')
    ai_research_insights = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            while True:
                part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                potential_ref = f"GBV-{part1}-{part2}"
                if not IncidentReport.objects.filter(reference_number=potential_ref).exists():
                    self.reference_number = potential_ref
                    break
        if not self.case_access_pin:
            self.case_access_pin = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_number} | {self.status.upper()}"

class AuditLog(models.Model):
    report = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)