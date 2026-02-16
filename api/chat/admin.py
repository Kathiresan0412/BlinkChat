from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, Report

User = get_user_model()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'is_banned', 'created_at')
    list_filter = ('is_banned',)
    search_fields = ('user__username', 'display_name')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'reason', 'reviewed', 'created_at')
    list_filter = ('reason', 'reviewed')
    search_fields = ('reporter__username', 'reported_user__username')
