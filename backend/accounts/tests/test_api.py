from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Profile

User = get_user_model()

LOGIN_URL = "/api/auth/login/"
LOGOUT_URL = "/api/auth/logout/"
ME_URL = "/api/auth/me/"
CSRF_URL = "/api/auth/csrf/"


def create_player(username, email, nickname, password="example-password"):
    user = User.objects.create_user(username=username, email=email, password=password)
    Profile.objects.create(user=user, nickname=nickname)
    return user


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_player("player_one", "player@example.com", "MountainKnight")

    def test_successful_login(self):
        response = self.client.post(
            LOGIN_URL,
            {"username": "player_one", "password": "example-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sessionid", response.cookies)
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.id))

        me = self.client.get(ME_URL)
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["id"], self.user.id)
        self.assertEqual(me.data["username"], "player_one")
        self.assertEqual(me.data["profile"]["nickname"], "MountainKnight")

    def test_failed_login(self):
        response = self.client.post(
            LOGIN_URL,
            {"username": "player_one", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertNotIn("_auth_user_id", self.client.session)

        me = self.client.get(ME_URL)
        self.assertIn(me.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class MePermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_player("player_one", "player@example.com", "MountainKnight")
        create_player("player_two", "other@example.com", "RiverKnight")

    def test_anonymous_access_is_denied(self):
        response = self.client.get(ME_URL)

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_authenticated_user_sees_only_own_data(self):
        self.client.force_login(self.user)

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], "player_one")
        self.assertEqual(response.data["email"], "player@example.com")
        self.assertEqual(response.data["profile"]["nickname"], "MountainKnight")
        self.assertNotIn("password", response.data)


class ProfileUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_player("player_one", "player@example.com", "MountainKnight")
        self.client.force_login(self.user)

    def test_update_profile(self):
        response = self.client.patch(
            ME_URL,
            {"nickname": "NewKnight", "avatar_key": "knight-3", "is_staff": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile"]["nickname"], "NewKnight")
        self.assertEqual(response.data["profile"]["avatar_key"], "knight-3")

        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nickname, "NewKnight")
        self.assertEqual(self.user.profile.avatar_key, "knight-3")
        self.assertFalse(self.user.is_staff)


class LogoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_player("player_one", "player@example.com", "MountainKnight")

    def test_logout(self):
        login = self.client.post(
            LOGIN_URL,
            {"username": "player_one", "password": "example-password"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)

        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn("_auth_user_id", self.client.session)

        me = self.client.get(ME_URL)
        self.assertIn(me.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class CsrfTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = create_player("player_one", "player@example.com", "MountainKnight")
        self.client.force_login(self.user)

    def test_unsafe_request_requires_csrf_token(self):
        data = {"nickname": "NewKnight"}

        without_token = self.client.patch(ME_URL, data, format="json")
        self.assertEqual(without_token.status_code, status.HTTP_403_FORBIDDEN)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nickname, "MountainKnight")

        csrf = self.client.get(CSRF_URL)
        self.assertEqual(csrf.status_code, status.HTTP_204_NO_CONTENT)
        token = self.client.cookies["csrftoken"].value

        with_token = self.client.patch(ME_URL, data, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(with_token.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nickname, "NewKnight")
