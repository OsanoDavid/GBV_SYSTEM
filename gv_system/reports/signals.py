from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import IncidentReport
from .analyzer import analyze_incident_text

@receiver(pre_save, sender=IncidentReport)
def run_automated_incident_triage(sender, instance, **kwargs):
    """
    Intercepts the IncidentReport right before database commit, 
    runs local NLP rules analysis, and assigns metrics to your updated model cache slots.
    """
    if instance.description and not instance.ai_classified_category:
        # Pass description directly into the logic module
        score, priority, tags = analyze_incident_text(instance.description)
        
        # FIXED MAP: Syncing directly to your newly configured choice schemas
        instance.ai_urgency_score = priority # Maps ('low', 'medium', 'high', 'critical')
        instance.ai_classified_category = instance.get_category_display()
        instance.ai_research_insights = f"Automated AI Assessment: Identified Key Abuse Vectors: [{tags}]."