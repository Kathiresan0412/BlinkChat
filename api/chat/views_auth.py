import logging
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .serializers import UserRegisterSerializer, UserProfileSerializer
from .models import UserProfile

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            logger.warning("Register IntegrityError: %s", e)
            return Response(
                {'detail': 'Username already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception("Register 500: %s", e)
            from django.conf import settings
            if settings.DEBUG:
                return Response(
                    {'detail': str(e), 'type': type(e).__name__},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            raise


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            data = {**UserProfileSerializer(profile).data, 'user_id': request.user.id}
        except UserProfile.DoesNotExist:
            data = {
                'username': request.user.username,
                'display_name': request.user.username,
                'created_at': None,
                'user_id': request.user.id,
            }
        return Response(data)
