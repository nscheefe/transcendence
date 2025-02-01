from django.db import models
from django.utils.timezone import now

# ChatRoom model
class ChatRoom(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-generated primary key
    name = models.CharField(max_length=255)  # Name of the chat room
    created_at = models.DateTimeField(default=now)  # Timestamp for when the room was created
    game_id = models.IntegerField(null=True, blank=True)  # Foreign key to the game (optional)

    def __str__(self):
        return self.name

# ChatRoomMessage model
class ChatRoomMessage(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-generated primary key
    content = models.TextField()  # Message content
    sender_id = models.IntegerField()  # Foreign key to the message sender (as user_id from another microservice)
    chat_room = models.ForeignKey(
        ChatRoom, related_name="messages", on_delete=models.CASCADE
    )  # Foreign key to the ChatRoom
    timestamp = models.DateTimeField(default=now)  # Timestamp of the message

    def __str__(self):
        return f"Message {self.id} in ChatRoom {self.chat_room}"

# ChatRoomUser model
class ChatRoomUser(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-generated primary key
    user_id = models.IntegerField()  # Foreign key to the User (via user_id from another service)
    chat_room = models.ForeignKey(
        ChatRoom, related_name="participants", on_delete=models.CASCADE
    )  # Foreign key to the ChatRoom
    joined_at = models.DateTimeField(default=now)  # Timestamp when the user joined the room
    class Meta:
        unique_together = [['user_id', 'chat_room']]
    def __str__(self):
        return f"User {self.user_id} in ChatRoom {self.chat_room}"
