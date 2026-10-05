from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from games.models import Game, Player

User = get_user_model()


def create_user(username):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="example-password",
    )


def add_players(game, count):
    colors = ["red", "green", "blue"]
    for i in range(count):
        Player.objects.create(
            user=create_user(f"player_{game.id}_{i}"),
            game=game,
            color=colors[i],
        )


class GameCreationTests(TestCase):
    def test_new_game_is_waiting(self):
        game = Game.objects.create()

        self.assertEqual(game.status, "waiting")
        self.assertIsNotNone(game.created_at)
        self.assertFalse(game.is_active())
        self.assertFalse(game.is_completed())

    def test_new_game_has_no_current_round(self):
        game = Game.objects.create()

        self.assertIsNone(game.get_current_round())


class GameStartTests(TestCase):
    def setUp(self):
        self.game = Game.objects.create()

    def test_start_with_three_players(self):
        add_players(self.game, 3)

        self.game.start()

        self.game.refresh_from_db()
        self.assertEqual(self.game.status, "active")
        self.assertTrue(self.game.is_active())

    def test_start_with_less_than_three_players(self):
        for count in [0, 1, 2]:
            with self.subTest(count=count):
                game = Game.objects.create()
                add_players(game, count)

                with self.assertRaises(ValidationError):
                    game.start()

                game.refresh_from_db()
                self.assertEqual(game.status, "waiting")

    def test_start_active_game(self):
        add_players(self.game, 3)
        self.game.start()

        with self.assertRaises(ValidationError):
            self.game.start()

    def test_complete_active_game(self):
        add_players(self.game, 3)
        self.game.start()

        self.game.complete()

        self.game.refresh_from_db()
        self.assertEqual(self.game.status, "completed")
        self.assertTrue(self.game.is_completed())

    def test_complete_waiting_game(self):
        with self.assertRaises(ValidationError):
            self.game.complete()

        self.game.refresh_from_db()
        self.assertEqual(self.game.status, "waiting")
