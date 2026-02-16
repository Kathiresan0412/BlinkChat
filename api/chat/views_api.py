from rest_framework import generics
from .models import Report
from .serializers import ReportSerializer


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
