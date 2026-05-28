"""
URL configuration for gv_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from reports import views as report_views



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core app handles landing and basic pages
    path('', include('core.urls')), 
    
    # Reports app handles filing, tracking, and portals
    path('', include('reports.urls')), 
    
    # Specific dashboard and admin mappings
    # Using 'user_dashboard_view' as defined in your views.py
    path('dashboard/', report_views.user_dashboard_view, name='user_dashboard'),
    
    # Using 'custom_admin_dashboard' as defined in your views.py
    path('command-center/', report_views.custom_admin_dashboard, name='custom_admin'),

   path('', include('reports.urls')), # This is the only place 'include' belongs
]