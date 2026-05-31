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
    
    # Reports app handles filing, tracking, and portals.
    # Make reports routes take precedence for /report/, /dashboard/, /portal/, etc.
    path('', include('reports.urls')),

    # Core app handles landing and other base pages.
    path('', include('core.urls')),

    # Specific admin command center mapping.
    path('command-center/', report_views.custom_admin_dashboard, name='custom_admin'),
]