from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard Landing Page - Synchronized with landing_page_view
    path('', views.landing_page_view, name='landing'),
    
    # 14-Point Implementation Module Route Mappings
    path('report/', views.file_report, name='file_report'),
    path('report/success/', views.report_success, name='report_success'),
    path('track/', views.track_case, name='track_case'),
    
    # Asynchronous AJAX Support Bot Communication Pipeline
    path('api/chat/', views.ai_assistant_chat, name='ai_assistant_chat'),
    
    # User Account Interfaces
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]