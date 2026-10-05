from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Game(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")

    def __str__(self):
        return f"Game {self.id} ({self.status})"

    def get_current_round(self):
        return self.rounds.order_by("-number").first()

    def is_active(self):
        return self.status == "active"

    def is_completed(self):
        return self.status == "completed"

    def start(self):
        if self.status != "waiting":
            raise ValidationError("Only a waiting game can be started.")
        if self.players.count() != 3:
            raise ValidationError("A game can be started only with exactly 3 players.")

        self.status = "active"
        self.full_clean()
        self.save()

    def complete(self):
        if self.status != "active":
            raise ValidationError("Only an active game can be completed.")

        self.status = "completed"
        self.full_clean()
        self.save()


class Player(models.Model):
    COLOR_CHOICES = [
        ("red", "Red"),
        ("green", "Green"),
        ("blue", "Blue"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    score = models.IntegerField(default=0)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "game"],
                name="unique_user_per_game",
            ),
            models.UniqueConstraint(
                fields=["game", "color"],
                name="unique_color_per_game",
            ),
            models.CheckConstraint(
                condition=models.Q(score__gte=0),
                name="player_score_gte_0",
            ),
        ]

    def __str__(self):
        return f"{self.user} in game {self.game_id} ({self.color})"

    def clean(self):
        if self.game_id is None or not self._state.adding:
            return

        if self.game.status != "waiting":
            raise ValidationError("Players can only be added while the game is waiting.")
        if self.game.players.count() >= 3:
            raise ValidationError("A game cannot have more than 3 players.")


class Round(models.Model):
    TYPE_CHOICES = [
        ("city_capture", "City capture"),
        ("battle", "Battle"),
        ("capital_attack", "Capital attack"),
        ("bonus", "Bonus"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    number = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    winner = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "number"],
                name="unique_round_number_per_game",
            ),
            models.UniqueConstraint(
                fields=["game"],
                condition=models.Q(status="active"),
                name="one_active_round_per_game",
            ),
            models.CheckConstraint(
                condition=~models.Q(status="completed") | models.Q(completed_at__isnull=False),
                name="completed_round_has_completed_at",
            ),
        ]

    def __str__(self):
        return f"Round {self.number} of game {self.game_id} ({self.type})"

    def clean(self):
        if self.game_id is None:
            return

        if self._state.adding and self.game.status == "completed":
            raise ValidationError("Rounds cannot be created in a completed game.")
        if self.winner_id is not None and self.winner.game_id != self.game_id:
            raise ValidationError("The winner must be a player from the same game.")
        if self.status == "completed" and self.completed_at is None:
            raise ValidationError("A completed round must have completed_at.")

    def start(self):
        if self.status != "pending":
            raise ValidationError("Only a pending round can be started.")

        self.status = "active"
        try:
            self.full_clean()
        except ValidationError:
            self.status = "pending"
            raise
        self.save()

    def complete(self, winner):
        if self.status != "active":
            raise ValidationError("Only an active round can be completed.")

        old_winner = self.winner
        self.winner = winner
        self.status = "completed"
        self.completed_at = timezone.now()
        try:
            self.full_clean()
        except ValidationError:
            self.winner = old_winner
            self.status = "active"
            self.completed_at = None
            raise
        self.save()
