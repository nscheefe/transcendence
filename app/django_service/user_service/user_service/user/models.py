from django.db import models

# Create your models here.
# user_service/models.py
from django.db import models

class Permission(models.Model):
    ADMIN = 0
    USER = 1
    PERMISSION_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    type = models.IntegerField(choices=PERMISSION_CHOICES)

class User(models.Model):
    name = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    permissions = models.ManyToManyField(Permission)
    isAuth = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)