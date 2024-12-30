from django.db import models

# Create your models here.
from django.db import models

class Auth(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=255)
    user_id = models.IntegerField()

class State(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=255)
