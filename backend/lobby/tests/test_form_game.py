from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, Player
from lobby.models import WaitingEntry
from lobby.views import form_game

User = get_user_model()


class FormGameTests(TestCase):
    def make_waiting(self, count):
        for i in range(count):
            user = User.objects.create_user(username=f"u{i}", email=f"u{i}@t.com", password="pass12345")
            WaitingEntry.objects.create(user=user)

    def test_five_waiting(self):
        self.make_waiting(5)
        game = form_game()

        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(game.status, "waiting")
        self.assertEqual(game.players.count(), 3)
        self.assertEqual(set(game.players.values_list("color", flat=True)), {"red", "green", "blue"})
        self.assertEqual(WaitingEntry.objects.count(), 2)

    def test_two_waiting(self):
        self.make_waiting(2)
        game = form_game()

        self.assertIsNone(game)
        self.assertEqual(Game.objects.count(), 0)
        self.assertEqual(Player.objects.count(), 0)
        self.assertEqual(WaitingEntry.objects.count(), 2)