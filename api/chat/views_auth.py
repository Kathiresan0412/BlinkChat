from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UserProfileSerializer
from .models import UserProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user_id': user.id,
            'username': user.username,
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            data = UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            data = {
                'username': request.user.username,
                'display_name': request.user.username,
                'created_at': None,
            }
        return Response(data)
