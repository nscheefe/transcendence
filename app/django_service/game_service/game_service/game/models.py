from django.db import models


# Create your models here.

class Game(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    state = models.CharField(max_length=255)  # State of the game
    points_player_a = models.IntegerField()  # Points scored by player A
    points_player_b = models.IntegerField()  # Points scored by player B
    player_a_id = models.IntegerField()  # Foreign Key to User for Player A
    player_b_id = models.IntegerField(blank=True, null=True)  # Foreign Key to User for Player B
    finished = models.BooleanField(default=False)  # Whether the game is finished
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of game creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp of last update

    def __str__(self):
        return f"Game {self.id}: {self.state}"


class GameEvent(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name="events")  # FK to Game
    event_type = models.CharField(max_length=255)  # Type of the event
    event_data = models.TextField()  # Data associated with the event
    timestamp = models.DateTimeField()  # Time of the event

    def __str__(self):
        return f"GameEvent {self.id} for Game {self.game_id}: {self.event_type}"
