from django.db import models
from datetime import datetime


class Stat(models.Model):
    """
    Represents a game statistic entry.
    """
    id = models.AutoField(primary_key=True)
    game_id = models.PositiveIntegerField(default=0)  # Default game ID
    winner_id = models.PositiveIntegerField(default=0)  # Foreign Key to the winner (User ID)
    loser_id = models.PositiveIntegerField(default=0)  # Foreign Key to the loser (User ID)
    created_at = models.DateTimeField(default=datetime.now)  # Timestamp with default value

    def __str__(self):
        return f"Stat {self.id}: Game {self.game_id} - Winner {self.winner_id}"


class UserStat(models.Model):
    """
    Represents a statistic record tied to a specific user.
    """
    id = models.AutoField(primary_key=True)
    user_id = models.PositiveIntegerField()  # Foreign Key to the user
    stat = models.ForeignKey(Stat, related_name="user_stats", on_delete=models.CASCADE)  # Foreign Key to the Stat
    did_win = models.BooleanField(default=False)  # Boolean indicating if the user won, defaults to False

    def __str__(self):
        return f"UserStat {self.id}: User {self.user_id} - {'Win' if self.did_win else 'Loss'}"
