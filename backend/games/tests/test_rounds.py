from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from games.models import Game, Player, Round

User = get_user_model()


def create_user(username):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="example-password",
    )


def create_active_game(prefix):
    game = Game.objects.create()
    for i, color in enumerate(["red", "green", "blue"]):
        Player.objects.create(user=create_user(f"{prefix}_{i}"), game=game, color=color)
    game.start()
    return game


class RoundCreationTests(TestCase):
    def setUp(self):
        self.game = create_active_game("player")

    def test_create_round(self):
        round = Round(game=self.game, number=1, type="city_capture")
        round.full_clean()
        round.save()

        self.assertEqual(round.game, self.game)
        self.assertEqual(round.number, 1)
        self.assertEqual(round.type, "city_capture")
        self.assertEqual(round.status, "pending")
        self.assertIsNone(round.winner)
        self.assertIsNotNone(round.created_at)
        self.assertIsNone(round.completed_at)

    def test_all_round_types(self):
        for number, round_type in enumerate(["city_capture", "battle", "capital_attack", "bonus"], 1):
            with self.subTest(type=round_type):
                round = Round(game=self.game, number=number, type=round_type)
                round.full_clean()
                round.save()

    def test_invalid_type(self):
        round = Round(game=self.game, number=1, type="duel")

        with self.assertRaises(ValidationError):
            round.full_clean()

    def test_duplicate_number_in_game(self):
        Round.objects.create(game=self.game, number=1, type="battle")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Round.objects.create(game=self.game, number=1, type="bonus")

    def test_same_number_in_different_games(self):
        other_game = create_active_game("other")
        Round.objects.create(game=self.game, number=1, type="battle")

        round = Round(game=other_game, number=1, type="battle")
        round.full_clean()
        round.save()

    def test_create_round_in_completed_game(self):
        self.game.complete()

        round = Round(game=self.game, number=1, type="battle")

        with self.assertRaises(ValidationError):
            round.full_clean()


class RoundCompletionTests(TestCase):
    def setUp(self):
        self.game = create_active_game("player")
        self.player = self.game.players.get(color="red")
        self.round = Round.objects.create(game=self.game, number=1, type="battle")

    def test_start_round(self):
        self.round.start()

        self.round.refresh_from_db()
        self.assertEqual(self.round.status, "active")

    def test_complete_round(self):
        self.round.start()

        self.round.complete(self.player)

        self.round.refresh_from_db()
        self.assertEqual(self.round.status, "completed")
        self.assertEqual(self.round.winner, self.player)
        self.assertIsNotNone(self.round.completed_at)

    def test_complete_pending_round(self):
        with self.assertRaises(ValidationError):
            self.round.complete(self.player)

    def test_winner_from_another_game(self):
        other_game = create_active_game("other")
        other_player = other_game.players.get(color="red")
        self.round.start()

        with self.assertRaises(ValidationError):
            self.round.complete(other_player)

        self.assertEqual(self.round.status, "active")
        self.assertIsNone(self.round.winner)
        self.round.refresh_from_db()
        self.assertEqual(self.round.status, "active")
        self.assertIsNone(self.round.winner)
        self.assertIsNone(self.round.completed_at)

    def test_completed_round_without_completed_at(self):
        with self.subTest("database"):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Round.objects.create(game=self.game, number=2, type="bonus", status="completed")

        with self.subTest("full_clean"):
            round = Round(game=self.game, number=2, type="bonus", status="completed")
            with self.assertRaises(ValidationError):
                round.full_clean()


class CurrentRoundTests(TestCase):
    def test_current_round_has_highest_number(self):
        game = create_active_game("player")
        Round.objects.create(game=game, number=2, type="battle")
        last = Round.objects.create(game=game, number=3, type="bonus")
        Round.objects.create(game=game, number=1, type="city_capture")

        self.assertEqual(game.get_current_round(), last)


class ActiveRoundTests(TestCase):
    def setUp(self):
        self.game = create_active_game("player")
        self.first = Round.objects.create(game=self.game, number=1, type="battle")
        self.second = Round.objects.create(game=self.game, number=2, type="bonus")
        self.first.start()

    def test_second_active_round(self):
        with self.assertRaises(ValidationError):
            self.second.start()

        self.assertEqual(self.second.status, "pending")
        self.second.refresh_from_db()
        self.assertEqual(self.second.status, "pending")

    def test_second_active_round_in_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Round.objects.filter(pk=self.second.pk).update(status="active")

    def test_next_round_after_completion(self):
        self.first.complete(self.game.players.get(color="red"))

        self.second.start()

        self.second.refresh_from_db()
        self.assertEqual(self.second.status, "active")

    def test_active_rounds_in_different_games(self):
        other_game = create_active_game("other")
        other_round = Round.objects.create(game=other_game, number=1, type="battle")

        other_round.start()

        self.assertEqual(other_round.status, "active")
