"""
URL configuration for BlinkChat backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api', RedirectView.as_view(url='/api/', permanent=False)),
    path('api/auth/', include('chat.urls_auth')),
    path('api/', include('chat.urls_api')),
]
