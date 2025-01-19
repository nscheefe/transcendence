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

class TournamentRoom(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    name = models.CharField(max_length=255)  # Name of the tournament room
    is_active = models.BooleanField(default=True)  # Whether the room is active
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of room creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp of last update

    def __str__(self):
        return f"TournamentRoom {self.id}: {self.name}"


class TournamentUser(models.Model):
    tournament_room = models.ForeignKey(
        'TournamentRoom',
        on_delete=models.CASCADE,
        related_name="participants"
    )
    user_id = models.IntegerField()  # Foreign Key to User (User ID)
    play_order = models.IntegerField()  # Index of the user in the order of play
    games_played = models.IntegerField(default=0)  # Number of games played by the user
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of record creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp of last update

    class Meta:
        # Define composite unique constraints
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "tournament_room"],
                name="unique_user_tournament"
            )
        ]

    def __str__(self):
        return f"TournamentUser: User {self.user_id} in TournamentRoom {self.tournament_room_id}"

class TournamentGameMapping(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    tournament_room = models.ForeignKey('TournamentRoom', on_delete=models.CASCADE,
                                        related_name="games")  # FK to TournamentRoom
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name="tournament_mappings")  # FK to Game
    user = models.ForeignKey('TournamentUser', on_delete=models.CASCADE,
                             related_name="user_game_mappings")  # FK to TournamentUser
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of record creation

    def __str__(self):
        return f"TournamentGameMapping {self.id}: Game {self.game_id} - User {self.user_id} in TournamentRoom {self.tournament_room_id}"
