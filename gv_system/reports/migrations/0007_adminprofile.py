# Generated migration for AdminProfile model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_rename_latitude_childrenshome_lat_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_level', models.CharField(choices=[('superadmin', 'Super Admin - Full System Access'), ('admin', 'Admin - Department Management'), ('assistant_admin', 'Assistant Admin - Report Management'), ('department_lead', 'Department Lead - Department-Specific Access')], default='admin', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('manages_departments', models.ManyToManyField(blank=True, related_name='admin_managers', to='reports.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
