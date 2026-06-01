import os, sys
# Discover project root by walking up until we find manage.py
script_dir = os.path.abspath(os.path.dirname(__file__))
cur = script_dir
project_root = None
while True:
    # Check for manage.py directly in this directory
    if os.path.exists(os.path.join(cur, 'manage.py')):
        project_root = cur
        break
    # Check for a 'gv_system' subdirectory containing manage.py (common layout)
    if os.path.exists(os.path.join(cur, 'gv_system', 'manage.py')):
        project_root = os.path.join(cur, 'gv_system')
        break
    parent = os.path.dirname(cur)
    if parent == cur:
        break
    cur = parent

if not project_root:
    # Fallback to parent of tools/ (best-effort)
    project_root = os.path.dirname(os.path.dirname(script_dir))

sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gv_system.settings')
print('Debug: project_root=', project_root)
print('Debug: sys.path[0]=', sys.path[0])
import django
try:
    django.setup()
except Exception as e:
    print('Failed to setup Django environment:', e)
    raise

from django.contrib.auth.models import User
from reports.models import IncidentReport

print('Users:')
for u in User.objects.all():
    print(u.id, u.username, repr(u.email))

linked_total = 0
for report in IncidentReport.objects.filter(reporter_profile__isnull=True):
    linked = False
    # Try match by email
    if report.reporter_email:
        users = User.objects.filter(email__iexact=report.reporter_email)
        if users.exists():
            user = users.first()
            report.reporter_profile = user
            report.save(update_fields=['reporter_profile'])
            linked = True
            linked_total += 1
            print(f"Linked report {report.reference_number} -> user {user.username} by email {report.reporter_email}")
    # Try match by reporter_name containing username
    if not linked and report.reporter_name:
        name_lower = report.reporter_name.lower()
        for u in User.objects.all():
            if u.username and u.username.lower() in name_lower:
                report.reporter_profile = u
                report.save(update_fields=['reporter_profile'])
                linked = True
                linked_total += 1
                print(f"Linked report {report.reference_number} -> user {u.username} by name match ({report.reporter_name})")
                break

print('Done. Total linked:', linked_total)
