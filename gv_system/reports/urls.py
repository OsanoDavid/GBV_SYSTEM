from django.urls import path
from .views import file_report_view, report_success_view, track_case_view, register_user_view, user_dashboard_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('report/', file_report_view, name='file_report'),
    path('report/success/<str:ref_num>/', report_success_view, name='report_success'),
    path('track/', track_case_view, name='track_case'),
    
    # Authentication & Dashboard Paths
    path('register/', register_user_view, name='register'),
    path('dashboard/', user_dashboard_view, name='user_dashboard'),
    path('login/', auth_views.LoginView.as_repr() if hasattr(auth_views.LoginView, 'as_repr') else auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
]