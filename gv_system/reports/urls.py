from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Core Base Views
    path('', views.landing_view, name='landing'),
    path('report/', views.file_report_view, name='file_report'),
    path('report/success/', views.report_success_view, name='report_success'),
    path('track/', views.track_case_view, name='track_case'),
    
    # Location-Based Assistance
    path('find-homes/', views.find_homes_view, name='find_homes'),
    
    # Authentication & Dashboard
    path('register/', views.register_user_view, name='register_user'),
    path('dashboard/', views.user_dashboard_view, name='user_dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    
    # Conversational API
    path('api/assistant/chat/', views.ai_assistant_chat_view, name='ai_assistant_chat'),

    # Portal & Admin
    path('portal/', views.department_portal_view, name='department_portal'),
    path('portal/update/<int:report_id>/', views.update_case_status, name='update_status'),
    path('admin-dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('edit-report/<int:report_id>/', views.friendly_edit_view, name='friendly_edit'),
    path('send-case-sms/<int:report_id>/', views.send_case_sms_view, name='send_case_sms'),
    path('delete-report/<int:report_id>/', views.delete_report_view, name='delete_report'),
]
