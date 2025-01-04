from django.db import models

class Auth(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
