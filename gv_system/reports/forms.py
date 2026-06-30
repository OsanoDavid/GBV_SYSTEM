from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.contrib.auth.models import User
from .models import IncidentReport


class SavedUserAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Username or email',
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    def clean(self):
        identifier = self.cleaned_data.get('username', '').strip()
        password = self.cleaned_data.get('password')

        if identifier and password:
            user_model = get_user_model()
            saved_user = (
                user_model._default_manager.filter(username__iexact=identifier).first()
                or user_model._default_manager.filter(email__iexact=identifier).first()
            )
            auth_username = saved_user.get_username() if saved_user else identifier
            self.user_cache = authenticate(
                self.request,
                username=auth_username,
                password=password,
            )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-3 bg-gray-50 border border-velvet-200 rounded-xl text-sm focus:ring-2 focus:ring-velvet-600 outline-none',
            'placeholder': 'Optional email used to link your past reports'
        }),
        help_text='Provide the same email you used when filing past cases so those reports appear in your dashboard.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SecureIncidentReportForm(forms.ModelForm):
    # Add a non-model field to capture custom category when "other" is selected
    custom_category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 bg-white border border-gray-200 rounded-xl text-xs font-medium text-gray-700 focus:ring-2 focus:ring-violet-600 outline-none',
            'placeholder': 'e.g., Cyber blackmail, Online scamming'
        })
    )

    class Meta:
        model = IncidentReport
        # Only list fields that exist in your models.py
        fields = [
            'incident_category', 'description', 'incident_date', 
            'platform_used', 'evidence_attachment', 'allow_contact', 
            'reporter_type', 'gender', 'age_group', 'disability', 
            'reporter_name', 'reporter_email', 'reporter_phone',
            'id_type', 'national_id_number', 'contact_mode', 'county',
            'constituency', 'ward', 'report_police', 'recommend_counseling',
            'consent_investigation'
        ]
        
        widgets = {
            'reporter_type': forms.Select(attrs={
                'class': 'w-full p-3 bg-gray-50 border border-velvet-200 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-velvet-600 transition outline-none font-medium text-gray-800'
            }),
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
                'list': 'platform-suggestions'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'w-full p-3 bg-white border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-600 text-sm',
                'placeholder': 'Please describe the incident in detail.'
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

        labels = {
            'reporter_name': 'Your Name (Optional)',
            'reporter_email': 'Secure Email Address (Optional)',
            'incident_category': 'What type of incident occurred?',
        }
