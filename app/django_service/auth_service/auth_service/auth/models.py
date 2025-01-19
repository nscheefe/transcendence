from django.db import models
from django.utils import timezone

class Auth(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.expires_at and timezone.is_naive(self.expires_at):
            self.expires_at = timezone.make_aware(self.expires_at, timezone.get_current_timezone())
        super().save(*args, **kwargs)
