import random
import string
from django.db import models
from django.contrib.auth.models import User

class IncidentReport(models.Model):
    CATEGORY_CHOICES = [
        ('cyberstalking', 'Cyberstalking & Harassment'),
        ('doxing', 'Non-Consensual Image Sharing / DoXing'),
        ('impersonation', 'Impersonation & Identity Theft'),
        ('threats', 'Online Threats & Hate Speech'),
        ('other', 'Other Forms of Online Abuse'),
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

    # --- Core Tracking Infrastructure ---
    reference_number = models.CharField(
        max_length=14, 
        unique=True, 
        editable=False, 
        db_index=True
    )
    
    # --- Dual Mode Login Association ---
    reporter_profile = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        help_text="Optional link to authenticated user profile."
    )

    # --- Incident Telemetry ---
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField()
    incident_date = models.DateField()
    platform_used = models.CharField(max_length=100, help_text="e.g., WhatsApp, X, Facebook, Email")
    evidence_attachment = models.FileField(upload_to='evidence/%Y/%m/%d/', blank=True, null=True)
    
    # Optional explicit contact strings (Includes requested phone number tracking)
    reporter_name = models.CharField(max_length=100, blank=True, null=True)
    reporter_email = models.EmailField(blank=True, null=True)
    reporter_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Optional contact number for alerts.")
    
    # --- Multi-Agent AI Metadata Cache ---
    ai_classified_category = models.CharField(max_length=50, blank=True, null=True)
    ai_urgency_score = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='low')
    ai_research_insights = models.TextField(
        blank=True, 
        null=True, 
        help_text="AI generated pattern matching and trend cross-referencing."
    )

    # --- Admin Lifecycle Management ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Override save workflow to generate a randomized, secure tracker hash code."""
        if not self.reference_number:
            while True:
                part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                potential_ref = f"GBV-{part1}-{part2}"
                
                # Verify uniqueness against database to prevent collisions
                if not IncidentReport.objects.filter(reference_number=potential_ref).exists():
                    self.reference_number = potential_ref
                    break
                    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_number} | {self.status.upper()}"