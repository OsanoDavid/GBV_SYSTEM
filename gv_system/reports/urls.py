from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    landing_view,
    file_report_view, 
    report_success_view, 
    track_case_view, 
    register_user_view, 
    user_dashboard_view,
    ai_assistant_chat_view,
    find_homes_view  # NEW: Added to support location-based search
)

urlpatterns = [
    # Core Base Views
    path('', landing_view, name='landing'),
    path('report/', file_report_view, name='file_report'),
    path('report/success/<str:ref_num>/', report_success_view, name='report_success'),
    path('track/', track_case_view, name='track_case'),
    
    # NEW: Location-Based Assistance
    path('find-homes/', find_homes_view, name='find_homes'),
    
    # Authentication & Dashboard Paths
    path('register/', register_user_view, name='register_user'),
    path('dashboard/', user_dashboard_view, name='user_dashboard'),
    
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    
    # Conversational System API Endpoint
    path('api/assistant/chat/', ai_assistant_chat_view, name='ai_assistant_chat'),
]