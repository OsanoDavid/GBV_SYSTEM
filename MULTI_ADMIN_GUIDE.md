# SafeSpace Multi-Admin System

## Overview

SafeSpace now supports a robust **multi-admin system** that allows multiple users to have full or partial system access with different permission levels. This document explains how to create, manage, and use admins.

---

## Quick Start: Create Your First Superuser

### Option 1: Using Django Management Command (Easiest)

```bash
cd gv_system
python manage.py create_superuser
```

Then enter:
- **Username**: `admin` (or your preferred username)
- **Email**: `admin@example.com`
- **Password**: Enter a strong password

✅ **Result**: User created with full system access

### Option 2: Using Django Shell

```bash
cd gv_system
python manage.py shell
```

Then in the shell:

```python
from django.contrib.auth.models import User
from reports.models import AdminProfile

# Create superuser
user = User.objects.create_superuser('admin', 'admin@example.com', 'password123')

# Automatically gets AdminProfile with 'superadmin' level
admin_profile = AdminProfile.objects.create(
    user=user,
    admin_level='superadmin',
    is_active=True
)

print(f"✅ Superuser {user.username} created with full system access")
```

### Option 3: Using the Admin Panel

1. Start Django server: `python manage.py runserver`
2. Go to `http://127.0.0.1:8000/admin`
3. Login with existing superuser
4. Click **Users** → **Add User**
5. Fill in username, email, password
6. Check **Staff status** and **Superuser status**
7. Save
8. Go to **Admin Profiles** → **Add Admin Profile**
9. Select the user and set admin level to **"Super Admin - Full System Access"**

---

## Admin Levels & Permissions

### 1️⃣ **Superadmin** (Full System Access)
- **Flag**: `is_superuser=True` in Django
- **Permissions**:
  - View ALL reports
  - Manage ALL departments
  - Create/delete other admins
  - Access all system settings
  - Full access to Command Center
- **Use Case**: System owner, lead administrator

### 2️⃣ **Admin** (Department Management)
- **Flag**: `admin_level='admin'` in AdminProfile
- **Permissions**:
  - View all reports
  - Manage assigned departments
  - Cannot create/delete admins
- **Use Case**: Regional manager, senior staff

### 3️⃣ **Assistant Admin** (Report Management)
- **Flag**: `admin_level='assistant_admin'` in AdminProfile
- **Permissions**:
  - View assigned department reports
  - Edit report details
  - Cannot manage other admins
- **Use Case**: Report specialist, analyst

### 4️⃣ **Department Lead** (Department-Specific Access)
- **Flag**: `admin_level='department_lead'` in AdminProfile
- **Permissions**:
  - Manage only their assigned departments
  - View only their department's reports
  - Cannot access system-wide settings
- **Use Case**: Department manager, local coordinator

---

## Creating Multiple Admins

### Using the Interactive Admin Tool

```bash
cd gv_system
python manage.py shell
```

Then:

```python
# For superuser
from tools.create_admins import create_superuser_interactive
create_superuser_interactive()

# For department admin
from tools.create_admins import create_admin_for_department
create_admin_for_department()

# List all admins
from tools.create_admins import list_all_admins
list_all_admins()
```

### Programmatic Creation

```python
from django.contrib.auth.models import User
from reports.models import AdminProfile, Department

# Create Superuser
superuser = User.objects.create_superuser('superadmin', 'super@example.com', 'pass123')
AdminProfile.objects.create(user=superuser, admin_level='superadmin')

# Create Department Admin
dept_admin = User.objects.create_user('dept_admin', 'deptadmin@example.com', 'pass123')
dept_admin.is_staff = True
dept_admin.save()

admin_profile = AdminProfile.objects.create(
    user=dept_admin,
    admin_level='admin',
    is_active=True
)

# Assign departments
dept = Department.objects.get(name='Gender-Based Violence Unit')
admin_profile.manages_departments.add(dept)
```

---

## Managing Admins via Admin Panel

### 1. View All Users

Navigate to: **Dashboard** → **Admin Profiles**

You'll see a table of all admins with:
- Username
- Admin Level
- Active Status
- Number of departments managed
- Created date

### 2. Create New Admin

**Users Section:**
1. Go to **Users** → **Add User**
2. Enter username, email, password
3. Check "Staff status" if needed
4. Save

**Assign Admin Profile:**
1. Go to **Admin Profiles** → **Add Admin Profile**
2. Select the user
3. Choose admin level
4. Assign departments (if applicable)
5. Save

### 3. Edit Existing Admin

1. Go to **Admin Profiles**
2. Click on the admin name
3. Update:
   - Admin level
   - Assigned departments
   - Active status
   - Notes
4. Save

### 4. Deactivate Admin

1. Go to **Admin Profiles**
2. Select the admin
3. Uncheck "Is active"
4. Save

❌ **Result**: User can still login but loses admin permissions

---

## Permission Checking in Code

Your app includes built-in helpers in `reports/views.py`:

```python
# Check if user is superadmin
if is_superadmin(request.user):
    # User has full system access
    pass

# Check if user can manage all reports
if can_manage_all_reports(request.user):
    # User is admin or superadmin
    pass

# Get departments user manages
departments = get_admin_departments(request.user)
# Returns all departments if superadmin, or specific departments if admin
```

---

## Examples

### Example 1: Create 3 Admins

```bash
python manage.py create_superuser --username admin1 --email admin1@example.com --password Admin@123

python manage.py create_superuser --username admin2 --email admin2@example.com --password Admin@456

python manage.py create_superuser --username admin3 --email admin3@example.com --password Admin@789
```

### Example 2: Create Department-Specific Admins

```python
from django.contrib.auth.models import User
from reports.models import AdminProfile, Department

# Get departments
gender_violence_dept = Department.objects.get(name='Gender-Based Violence Unit')
cyber_abuse_dept = Department.objects.get(name='Cyber Abuse Unit')

# Create admin for Gender Violence
user1 = User.objects.create_user('gbv_admin', 'gbv@example.com', 'pass123')
user1.is_staff = True
user1.save()

admin1 = AdminProfile.objects.create(user=user1, admin_level='admin')
admin1.manages_departments.add(gender_violence_dept)

# Create admin for Cyber Abuse
user2 = User.objects.create_user('cyber_admin', 'cyber@example.com', 'pass123')
user2.is_staff = True
user2.save()

admin2 = AdminProfile.objects.create(user=user2, admin_level='admin')
admin2.manages_departments.add(cyber_abuse_dept)
```

### Example 3: Query All Superadmins

```python
from reports.models import AdminProfile

superadmins = AdminProfile.objects.filter(
    admin_level='superadmin',
    is_active=True
)

for admin in superadmins:
    print(f"{admin.user.username} - {admin.get_admin_level_display()}")
```

---

## Security Best Practices

1. **Strong Passwords**: Use password manager to generate strong passwords
2. **Minimal Privileges**: Only give admin access to trusted users
3. **Audit Trail**: All admin actions are logged in AuditLog
4. **Inactive Admins**: Deactivate admins when they leave, don't delete
5. **Periodic Review**: Regularly review who has admin access

---

## Troubleshooting

### "Can't create superuser - IntegrityError"
**Problem**: Username already exists

**Solution**: 
```bash
# Check existing users
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all().values_list('username', flat=True)

# Use a different username
```

### "Admin panel shows no AdminProfile"
**Problem**: Migration not applied

**Solution**:
```bash
python manage.py makemigrations
python manage.py migrate
```

### "User has admin created but can't see it in panel"
**Problem**: AdminProfile not created for existing user

**Solution**:
```python
from django.contrib.auth.models import User
from reports.models import AdminProfile

user = User.objects.get(username='myuser')
AdminProfile.objects.create(user=user, admin_level='admin')
```

---

## Next Steps

- ✅ Create your first superuser
- ✅ Login to admin panel
- ✅ Create additional admins with different levels
- ✅ Assign departments to department-level admins
- ✅ Test permissions

Need help? Check the Django admin interface at `/admin` or review `reports/models.py` for AdminProfile structure.
