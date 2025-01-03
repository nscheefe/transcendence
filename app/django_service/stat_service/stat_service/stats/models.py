from django.db import models

class Stat(models.Model):
    """
    Represents a game statistic entry.
    """
    id = models.AutoField(primary_key=True)
    game_id = models.PositiveIntegerField()  # Foreign Key to the game (not enforced in this schema)
    winner_id = models.PositiveIntegerField()  # Foreign Key to the winner (User ID)
    loser_id = models.PositiveIntegerField()  # Foreign Key to the loser (User ID)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set timestamp when created

    def __str__(self):
        return f"Stat {self.id}: Game {self.game_id} - Winner {self.winner_id}"


class UserStat(models.Model):
    """
    Represents a statistic record tied to a specific user.
    """
    id = models.AutoField(primary_key=True)
    user_id = models.PositiveIntegerField()  # Foreign Key to the user
    stat = models.ForeignKey(Stat, related_name="user_stats", on_delete=models.CASCADE)  # Foreign Key to the Stat
    did_win = models.BooleanField()  # Boolean indicating if the user won the game

    def __str__(self):
        return f"UserStat {self.id}: User {self.user_id} - {'Win' if self.did_win else 'Loss'}"
