from django.db import models
from django.contrib.auth.models import Group
import uuid
import secrets

# ==========================================
# 1. INCIDENT MANAGEMENT ENGINE (Points 2, 3, 4, 9)
# ==========================================

class IncidentReport(models.Model):
    # Demographics Choice Arrays (Point 3)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-Binary'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    AGE_CHOICES = [
        ('U18', 'Under 18 years'),
        ('18-24', '18 - 24 years'),
        ('25-34', '25 - 34 years'),
        ('35-44', '35 - 44 years'),
        ('45+', '45 years and above'),
    ]
    
    DISABILITY_CHOICES = [
        ('none', 'No disability condition'),
        ('visual', 'Visual impairment'),
        ('hearing', 'Hearing impairment'),
        ('mobility', 'Physical/Mobility impairment'),
        ('cognitive', 'Cognitive/Intellectual impairment'),
        ('other', 'Other constraint variants'),
    ]

    # Proxy Reporting Types (Point 4)
    REPORTER_TYPE_CHOICES = [
        ('self', 'Reporting for Myself'),
        ('victim_adult', 'Reporting on behalf of another Adult'),
        ('child', 'Reporting on behalf of a Minor/Child'),
    ]

    # Leveling & Triage Classifications (Point 9)
    SEVERITY_LEVELS = [
        ('LOW', 'Low Risk - Routine Monitoring'),
        ('MEDIUM', 'Medium Risk - Administrative Action Required'),
        ('HIGH', 'High Risk - Immediate Legal/Medical Intervention'),
        ('CRITICAL', 'Critical Crisis - Law Enforcement Dispatch'),
    ]

    # Unique Reference System (No predictable auto-increment integers)
    reference_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    
    # Hashed/Plain Track Token for Anonymous View Verification (Point 2)
    case_access_pin = models.CharField(max_length=12, editable=False)

    # Context Dynamic Variables (Points 3 & 4)
    reporter_type = models.CharField(max_length=15, choices=REPORTER_TYPE_CHOICES, default='self')
    allow_contact = models.BooleanField(default=False, help_text="Can our care teams reach back out to you?")
    contact_detail = models.CharField(max_length=150, blank=True, null=True, help_text="WhatsApp / Email / Phone link string")
    
    # Target Identity Attributes
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default='P')
    age_group = models.CharField(max_length=10, choices=AGE_CHOICES)
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default='none')

    # Threat Profiling Information
    incident_category = models.CharField(max_length=50) # cyberstalking, doxing, impersonation, hate_speech, theft
    description = models.TextField()
    is_child_directed = models.BooleanField(default=False, editable=False)

    # Workflow & Custom Escalation Leveling (Point 9)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='LOW')
    assigned_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_incidents")
    status = models.CharField(max_length=20, default='Submitted', choices=[
        ('Submitted', 'Submitted & Triaging'),
        ('In_Review', 'Under Review'),
        ('Assigned', 'Routed to Specialist'),
        ('Action_Taken', 'Intervention Complete'),
        ('Closed', 'Archived Secured')
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *origin_arguments, **origin_keyword_arguments):
        # Auto-generate a secure tracking pin if it doesn't exist yet
        if not self.case_access_pin:
            self.case_access_pin = secrets.token_hex(4).upper() # Creates an 8-character string (e.g., A4B27D9E)
        
        # Point 4 Rule Execution: Automatically tag minor reporting pipelines
        if self.reporter_type == 'child' or self.age_group == 'U18':
            self.is_child_directed = True
            self.severity = 'HIGH' # Instantly elevate priority status

        super().save(*origin_arguments, **origin_keyword_arguments)

    def __str__(self):
        return f"Ref: {self.reference_number.hex[:8].upper()} | Cat: {self.incident_category} | Status: {self.status}"


# ==========================================
# 2. AI LIVE CONVERSATIONAL TRACKS
# ==========================================

class HelpChatSession(models.Model):
    session_token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Session {self.session_token[:8]}"

class ChatMessage(models.Model):
    session = models.ForeignKey(HelpChatSession, on_delete=models.CASCADE, related_name="messages")
    is_from_user = models.BooleanField(default=True)
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "User" if self.is_from_user else "AI Assistant"
        return f"{sender} at {self.timestamp.strftime('%H:%M:%S')}"