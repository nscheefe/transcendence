import json
from django.db import models
from django.utils import timezone

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    mail = models.EmailField()
    isAuth = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    role_id = models.IntegerField()
    last_login = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.CharField(max_length=45, blank=True)

class Friendship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_friendships')
    established_at = models.DateTimeField(default=timezone.now)
    accepted = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'friend')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now)

class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_url = models.URLField(max_length=1024)
    nickname = models.CharField(max_length=255, unique=True)
    bio = models.TextField(blank=True)
    additional_info = models.TextField()

    def set_additional_info(self, data):
        self.additional_info = json.dumps(data)

    def get_additional_info(self):
        return json.loads(self.additional_info)

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'permission')

class Setting(models.Model):
    name = models.CharField(max_length=255)
    data = models.TextField()  # JSON data serialized as a string
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'user')

    def set_data(self, data):
        self.data = json.dumps(data)

    def get_data(self):
        return json.loads(self.data)

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement_id = models.IntegerField()
    unlocked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'achievement_id')
