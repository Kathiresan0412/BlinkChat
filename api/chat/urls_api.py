from django.urls import path
from .views_api import ReportCreateView, api_root

urlpatterns = [
    path('', api_root),
    path('reports/', ReportCreateView.as_view(), name='report-create'),
]
