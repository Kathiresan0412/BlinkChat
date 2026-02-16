from django.urls import path
from .views_api import ReportCreateView

urlpatterns = [
    path('reports/', ReportCreateView.as_view(), name='report-create'),
]
