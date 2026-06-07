from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError
from reports.models import AdminProfile


class Command(BaseCommand):
    help = 'Create multiple superusers with full system access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')

        if not username:
            username = input('Enter username: ').strip()
        
        if not email:
            email = input('Enter email: ').strip()
        
        if not password:
            password = input('Enter password: ').strip()

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            # Automatically create AdminProfile with superadmin level
            admin_profile, created = AdminProfile.objects.get_or_create(
                user=user,
                defaults={
                    'admin_level': 'superadmin',
                    'is_active': True,
                    'notes': f'Superuser created via management command'
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser "{username}" created successfully with full system access!'
                )
            )
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error: Username "{username}" already exists!'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {str(e)}')
            )
