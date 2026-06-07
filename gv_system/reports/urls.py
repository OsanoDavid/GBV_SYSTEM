from django.urls import path, reverse_lazy
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
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
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
