import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, Report

User = get_user_model()

# Django username: letters, numbers, @/./+/-/_ only
USERNAME_ALLOWED = re.compile(r'^[\w.@+-]+\Z', re.UNICODE)


def sanitize_username(value):
    """Convert to valid Django username: replace spaces with _, remove disallowed chars."""
    if not value or not isinstance(value, str):
        return value
    s = value.strip().replace(' ', '_')
    s = ''.join(c for c in s if USERNAME_ALLOWED.match(c) or c in '.@+-')
    return s or value.strip().replace(' ', '_')[:150]


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'display_name', 'created_at')
        read_only_fields = fields


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True, default='')

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Username is required.')
        sanitized = sanitize_username(value)
        if len(sanitized) > 150:
            sanitized = sanitized[:150]
        if not sanitized:
            raise serializers.ValidationError(
                'Username may contain only letters, numbers, and @/./+/-/_ characters.'
            )
        return sanitized

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        UserProfile.objects.get_or_create(user=user, defaults={'display_name': user.username})
        return user


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'reported_user', 'reason', 'description', 'session_id', 'created_at')
        read_only_fields = ('reporter', 'created_at')
