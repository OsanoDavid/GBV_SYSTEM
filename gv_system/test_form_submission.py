#!/usr/bin/env python
"""
Quick test to verify form submission works without errors.
Run from gv_system directory: python test_form_submission.py
"""
import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gv_system.settings')
django.setup()

from reports.forms import SecureIncidentReportForm
from reports.models import IncidentReport
from datetime import date

def test_form_with_standard_category():
    """Test form submission with a standard incident category."""
    print("\n=== Test 1: Standard Category (Cyberstalking) ===")
    form_data = {
        'incident_category': 'cyberstalking',
        'description': 'This is a test incident with sufficient detail to pass validation.',
        'incident_date': date.today().isoformat(),
        'platform_used': 'WhatsApp',
        'reporter_type': 'self',
        'gender': 'F',
        'age_group': '25-34',
        'disability': 'none',
        'allow_contact': False,
    }
    form = SecureIncidentReportForm(form_data)
    if form.is_valid():
        print("✓ Form is valid!")
        print(f"  Cleaned data incident_category: {form.cleaned_data['incident_category']}")
        return True
    else:
        print("✗ Form is invalid!")
        print(f"  Errors: {form.errors}")
        return False

def test_form_with_other_category():
    """Test form submission with 'other' category and custom text."""
    print("\n=== Test 2: Other Category with Custom Text ===")
    form_data = {
        'incident_category': 'other',
        'custom_category': 'Cyber blackmail attempt',
        'description': 'This is a test incident with sufficient detail to pass validation.',
        'incident_date': date.today().isoformat(),
        'platform_used': 'Instagram',
        'reporter_type': 'self',
        'gender': 'M',
        'age_group': '18-24',
        'disability': 'none',
        'allow_contact': False,
    }
    form = SecureIncidentReportForm(form_data)
    if form.is_valid():
        print("✓ Form is valid!")
        print(f"  Cleaned data incident_category: {form.cleaned_data['incident_category']}")
        print(f"  Cleaned data custom_category: {form.cleaned_data['custom_category']}")
        return True
    else:
        print("✗ Form is invalid!")
        print(f"  Errors: {form.errors}")
        return False

def test_form_with_threats_category():
    """Test form submission with updated threats category."""
    print("\n=== Test 3: Threats Category ===")
    form_data = {
        'incident_category': 'threats',
        'description': 'This is a test incident with sufficient detail to pass validation.',
        'incident_date': date.today().isoformat(),
        'platform_used': 'X (Twitter)',
        'reporter_type': 'self',
        'gender': 'P',
        'age_group': '35-44',
        'disability': 'none',
        'allow_contact': False,
    }
    form = SecureIncidentReportForm(form_data)
    if form.is_valid():
        print("✓ Form is valid!")
        print(f"  Cleaned data incident_category: {form.cleaned_data['incident_category']}")
        return True
    else:
        print("✗ Form is invalid!")
        print(f"  Errors: {form.errors}")
        return False

if __name__ == '__main__':
    print("Testing SecureIncidentReportForm...")
    
    results = []
    results.append(("Standard Category", test_form_with_standard_category()))
    results.append(("Other Category", test_form_with_other_category()))
    results.append(("Threats Category", test_form_with_threats_category()))
    
    print("\n" + "="*50)
    print("Test Results:")
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    exit(0 if all_passed else 1)
