from django import forms
from .models import IncidentReport

class SecureIncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        # Expose only public incident entry metrics
        fields = ['category', 'description', 'incident_date', 'platform_used', 'evidence_attachment', 'reporter_name', 'reporter_email']
        
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5, 
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm',
                'placeholder': 'Please describe the incident in detail. For your safety, do not include passwords or highly sensitive credentials.'
            }),
            'incident_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm'
            }),
            'platform_used': forms.TextInput(attrs={
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm',
                'placeholder': 'e.g., WhatsApp, Instagram, Facebook, X'
            }),
            
            # FIXED HERE: Changed forms.TextInput field logic to forms.TextInput widget
            'reporter_name': forms.TextInput(attrs={
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm',
                'placeholder': 'Optional (Leave completely blank to report anonymously)'
            }),
            
            # FIXED HERE: Changed forms.EmailField (Field) to forms.EmailInput (Widget)
            'reporter_email': forms.EmailInput(attrs={
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm',
                'placeholder': 'Optional (For automated case update alerts)'
            }),
            
            'evidence_attachment': forms.FileInput(attrs={
                'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100'
            }),
        }