from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import Profile

User = get_user_model()


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="player_one",
            email="player@example.com",
            password="example-password",
        )
        self.profile = Profile.objects.create(user=self.user, nickname="MountainKnight")

    def test_user_has_profile_with_default_avatar(self):
        self.assertEqual(self.user.profile, self.profile)
        self.assertEqual(self.user.profile.nickname, "MountainKnight")
        self.assertEqual(self.user.profile.avatar_key, "knight-1")

    def test_email_and_nickname_are_unique(self):
        other = User.objects.create_user(
            username="player_two",
            email="other@example.com",
            password="example-password",
        )

        with self.subTest("email"):
            with self.assertRaises(IntegrityError), transaction.atomic():
                User.objects.create_user(
                    username="player_three",
                    email="player@example.com",
                    password="example-password",
                )

        with self.subTest("nickname"):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Profile.objects.create(user=other, nickname="MountainKnight")
