"""
URL configuration for BlinkChat backend.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('chat.urls_auth')),
    path('api/', include('chat.urls_api')),
]
