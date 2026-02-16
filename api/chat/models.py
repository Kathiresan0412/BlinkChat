"""
Models for user profiles, reports, and moderation.
"""
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=64, blank=True)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username or str(self.user.id)


class Report(models.Model):
    REPORT_REASONS = [
        ('inappropriate', 'Inappropriate content'),
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('underage', 'Underage'),
        ('other', 'Other'),
    ]
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_against')
    reason = models.CharField(max_length=32, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    session_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
