from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile
from accounts.serializers import RegisterSerializer

User = get_user_model()


def registration_data(**overrides):
    data = {
        "username": "player_one",
        "email": "player@example.com",
        "nickname": "MountainKnight",
        "password": "example-password",
        "password_confirm": "example-password",
    }
    data.update(overrides)
    return data


class RegisterSerializerTests(TestCase):
    def test_successful_registration(self):
        serializer = RegisterSerializer(data=registration_data())

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertTrue(User.objects.filter(username="player_one").exists())
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.email, "player@example.com")
        self.assertEqual(user.profile.nickname, "MountainKnight")
        self.assertTrue(user.check_password("example-password"))
        self.assertNotEqual(user.password, "example-password")

        self.assertNotIn("password", serializer.data)
        self.assertNotIn("password_confirm", serializer.data)
        self.assertEqual(serializer.data["profile"]["nickname"], "MountainKnight")

    def test_invalid_registration(self):
        existing = User.objects.create_user(
            username="taken_user",
            email="taken@example.com",
            password="example-password",
        )
        Profile.objects.create(user=existing, nickname="TakenKnight")

        cases = [
            ("username", registration_data(username="taken_user")),
            ("email", registration_data(email="taken@example.com")),
            ("nickname", registration_data(nickname="TakenKnight")),
            ("password_confirm", registration_data(password_confirm="other-password")),
        ]

        for field, data in cases:
            with self.subTest(field=field):
                serializer = RegisterSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)
                self.assertEqual(User.objects.count(), 1)
                self.assertEqual(Profile.objects.count(), 1)
