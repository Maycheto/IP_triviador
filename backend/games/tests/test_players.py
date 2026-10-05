from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from games.models import Game, Player

User = get_user_model()


def create_user(username):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="example-password",
    )


class AddPlayersTests(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.users = [create_user(f"player_{i}") for i in range(4)]

    def test_add_three_players(self):
        for user, color in zip(self.users, ["red", "green", "blue"]):
            player = Player(user=user, game=self.game, color=color)
            player.full_clean()
            player.save()

        players = self.game.players.all()
        self.assertEqual(players.count(), 3)
        self.assertEqual({p.color for p in players}, {"red", "green", "blue"})
        self.assertEqual(len({p.user_id for p in players}), 3)
        for player in players:
            self.assertEqual(player.score, 0)

    def test_fourth_player(self):
        for user, color in zip(self.users, ["red", "green", "blue"]):
            Player.objects.create(user=user, game=self.game, color=color)

        player = Player(user=self.users[3], game=self.game, color="red")

        with self.assertRaises(ValidationError):
            player.full_clean()

    def test_add_player_to_active_game(self):
        self.game.status = "active"
        self.game.save()

        player = Player(user=self.users[0], game=self.game, color="red")

        with self.assertRaises(ValidationError):
            player.full_clean()

    def test_same_user_and_color_in_different_games(self):
        other_game = Game.objects.create()
        Player.objects.create(user=self.users[0], game=self.game, color="red")

        player = Player(user=self.users[0], game=other_game, color="red")
        player.full_clean()
        player.save()

        self.assertEqual(Player.objects.filter(user=self.users[0]).count(), 2)

    def test_change_score_in_active_game(self):
        for user, color in zip(self.users, ["red", "green", "blue"]):
            Player.objects.create(user=user, game=self.game, color=color)
        self.game.start()

        player = self.game.players.get(color="red")
        player.score = 10
        player.full_clean()
        player.save()

        player.refresh_from_db()
        self.assertEqual(player.score, 10)


class InvalidPlayerTests(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.user = create_user("player_one")
        self.other_user = create_user("player_two")
        Player.objects.create(user=self.user, game=self.game, color="red")

    def test_duplicate_user_in_game(self):
        with self.subTest("database"):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Player.objects.create(user=self.user, game=self.game, color="green")

        with self.subTest("full_clean"):
            player = Player(user=self.user, game=self.game, color="green")
            with self.assertRaises(ValidationError):
                player.full_clean()

    def test_duplicate_color_in_game(self):
        with self.subTest("database"):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Player.objects.create(user=self.other_user, game=self.game, color="red")

        with self.subTest("full_clean"):
            player = Player(user=self.other_user, game=self.game, color="red")
            with self.assertRaises(ValidationError):
                player.full_clean()

    def test_negative_score(self):
        with self.subTest("database"):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Player.objects.create(
                    user=self.other_user, game=self.game, color="green", score=-1
                )

        with self.subTest("full_clean"):
            player = Player(user=self.other_user, game=self.game, color="green", score=-1)
            with self.assertRaises(ValidationError):
                player.full_clean()

    def test_invalid_color(self):
        player = Player(user=self.other_user, game=self.game, color="yellow")

        with self.assertRaises(ValidationError):
            player.full_clean()
