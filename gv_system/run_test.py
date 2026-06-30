import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gv_system.settings')
django.setup()

from django.test import Client
from reports.models import IncidentReport

# 1. Setup client
client = Client()

# 2. Test Submission Data
data = {
    'reporter_name': 'Test User',
    'gender': 'Female',
    'id_type_selection': 'National ID',
    'national_id_number': '12345678',
    'age_group': '18-24',
    'contact_mode': 'Phone Number',
    'contact_info': '0712345678',
    'disability': 'No condition',
    'incident_category': 'Cyberstalking',
    'platform_used': 'WhatsApp',
    'description': 'Someone keeps calling me from random numbers.',
    'report_police': 'on',
    'recommend_counseling': 'on',
    'allow_contact': 'on', 
    'consent_investigation': 'on',
    'county': 'Nairobi',
    'constituency': 'Westlands',
    'ward': 'Kangemi'
}

response = client.post('/report/', data)
print(f"Status Code: {response.status_code}")

latest_report = IncidentReport.objects.last()
if latest_report:
    print(f"Submitting worked! Created Instance ID: {latest_report.id}")
    print(f"PIN: {latest_report.case_access_pin}")
    print(f"Phone logged: {latest_report.reporter_phone}")
    print(f"County logged: {latest_report.county}")
    
    # Check AuditLogs for SMS
    logs = latest_report.audit_logs.all()
    for log in logs:
        print(f"AuditLog Action: {log.action}")
else:
    print("Report was not created successfully.")
