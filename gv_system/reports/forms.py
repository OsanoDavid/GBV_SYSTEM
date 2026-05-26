from django import forms
from .models import IncidentReport

class SecureIncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        # Expose all public entry metrics processed by the multi-step form wizard
        fields = [
            'reporter_type', 'incident_category', 'gender', 'age_group', 'disability',
            'incident_date', 'platform_used', 'description', 'evidence_attachment', 
            'allow_contact', 'reporter_name', 'reporter_email', 'reporter_phone'
        ]
        
        widgets = {
            'reporter_type': forms.Select(attrs={
                'class': 'w-full p-3 bg-gray-50 border border-velvet-200 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-velvet-600 transition outline-none font-medium text-gray-800'
            }),
            # Updated from 'category' to 'incident_category' matching the revised DB model
            'incident_category': forms.Select(attrs={
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full p-3 bg-gray-50 border border-velvet-200 rounded-xl text-xs font-medium text-gray-700 focus:bg-white focus:ring-2 focus:ring-velvet-600 outline-none'
            }),
            'age_group': forms.Select(attrs={
                'class': 'w-full p-3 bg-gray-50 border border-velvet-200 rounded-xl text-xs font-medium text-gray-700 focus:bg-white focus:ring-2 focus:ring-velvet-600 outline-none'
            }),
            'disability': forms.Select(attrs={
                'class': 'w-full p-3 bg-gray-50 border border-velvet-200 rounded-xl text-xs font-medium text-gray-700 focus:bg-white focus:ring-2 focus:ring-velvet-600 outline-none'
            }),
            'incident_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm'
            }),
            'platform_used': forms.TextInput(attrs={
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm',
                'placeholder': 'e.g., WhatsApp, Instagram, Facebook, X',
                'list': 'platform-suggestions'  # Binds smoothly to HTML5 datalist
            }),
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm',
                'placeholder': 'Please describe the incident in detail. For your safety, do not include passwords or highly sensitive credentials.'
            }),
            'evidence_attachment': forms.FileInput(attrs={
                'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100'
            }),
            'allow_contact': forms.CheckboxInput(attrs={
                'class': 'rounded text-velvet-600 focus:ring-velvet-500 w-4 h-4 mr-2.5'
            }),
            'reporter_name': forms.TextInput(attrs={
                'class': 'w-full p-2.5 bg-white border border-velvet-200 rounded-xl text-xs focus:ring-2 focus:ring-velvet-600 outline-none',
                'placeholder': 'Optional handle'
            }),
            'reporter_email': forms.EmailInput(attrs={
                'class': 'w-full p-2.5 bg-white border border-velvet-200 rounded-xl text-xs focus:ring-2 focus:ring-velvet-600 outline-none',
                'placeholder': 'Optional secure mail'
            }),
            'reporter_phone': forms.TextInput(attrs={
                'class': 'w-full p-2.5 bg-white border border-velvet-200 rounded-xl text-xs focus:ring-2 focus:ring-velvet-600 outline-none',
                'placeholder': 'Optional phone/sms alerts'
            }),
        }