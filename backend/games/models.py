from django.conf import settings
from django.db import models


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
