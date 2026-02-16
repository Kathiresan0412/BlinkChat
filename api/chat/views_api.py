from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Simple API root so GET /api/ returns 200 without auth."""
    return Response({'ok': True})


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
