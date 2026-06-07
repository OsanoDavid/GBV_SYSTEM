"""
Script to create multiple superusers or admins with full system access
Run this from the manage.py shell:
    
    python manage.py shell < tools/create_admins.py

Or directly:
    
    python manage.py create_superuser --username admin1 --email admin1@example.com --password yourpassword
"""

from django.contrib.auth.models import User
from reports.models import AdminProfile, Department

def create_superuser_interactive():
    """Interactive superuser creation"""
    print("\n=== CREATE SUPERUSER (Full System Access) ===\n")
    
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    
    if User.objects.filter(username=username).exists():
        print(f"❌ Username '{username}' already exists!")
        return
    
    user = User.objects.create_superuser(username, email, password)
    
    # Automatically create AdminProfile
    admin_profile = AdminProfile.objects.create(
        user=user,
        admin_level='superadmin',
        is_active=True,
        notes=f'Created as superuser on {user.date_joined.strftime("%Y-%m-%d %H:%M")}'
    )
    
    print(f"\n✅ Superuser '{username}' created successfully!")
    print(f"   Admin Level: {admin_profile.get_admin_level_display()}")
    print(f"   Full System Access: Yes\n")


def create_admin_for_department():
    """Create an admin for specific departments"""
    print("\n=== CREATE DEPARTMENT ADMIN ===\n")
    
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    
    if User.objects.filter(username=username).exists():
        print(f"❌ Username '{username}' already exists!")
        return
    
    # Create user with staff privileges
    user = User.objects.create_user(username, email, password)
    user.is_staff = True
    user.save()
    
    # Show available departments
    departments = Department.objects.all()
    print(f"\nAvailable departments ({departments.count()}):")
    for i, dept in enumerate(departments, 1):
        print(f"  {i}. {dept.name}")
    
    dept_ids = input("Enter department numbers (comma-separated, e.g. 1,2,3): ").strip()
    selected_departments = []
    
    for dept_id in dept_ids.split(','):
        try:
            dept = departments[int(dept_id.strip()) - 1]
            selected_departments.append(dept)
        except (ValueError, IndexError):
            print(f"⚠️  Invalid selection: {dept_id}")
    
    # Create AdminProfile
    admin_profile = AdminProfile.objects.create(
        user=user,
        admin_level='admin',
        is_active=True,
        notes=f'Department admin created on {user.date_joined.strftime("%Y-%m-%d %H:%M")}'
    )
    admin_profile.manages_departments.set(selected_departments)
    
    print(f"\n✅ Department Admin '{username}' created successfully!")
    print(f"   Admin Level: {admin_profile.get_admin_level_display()}")
    print(f"   Manages {selected_departments.count()} department(s)")
    print(f"   Departments: {', '.join([d.name for d in selected_departments])}\n")


def list_all_admins():
    """List all current admins"""
    print("\n=== ALL SYSTEM ADMINS ===\n")
    admins = AdminProfile.objects.select_related('user').all()
    
    if not admins:
        print("No admins found in the system.\n")
        return
    
    for admin in admins:
        status = "✅ Active" if admin.is_active else "❌ Inactive"
        print(f"{admin.user.username:20} | {admin.get_admin_level_display():40} | {status}")
        if admin.manages_departments.exists():
            depts = ", ".join([d.name for d in admin.manages_departments.all()])
            print(f"  → Manages: {depts}")
    print()


if __name__ == "__main__":
    while True:
        print("\n=== ADMIN MANAGEMENT MENU ===")
        print("1. Create new superuser (full system access)")
        print("2. Create department admin")
        print("3. List all admins")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            create_superuser_interactive()
        elif choice == '2':
            create_admin_for_department()
        elif choice == '3':
            list_all_admins()
        elif choice == '4':
            print("\nGoodbye!\n")
            break
        else:
            print("❌ Invalid option!")
