from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """

    :param params:
    :return:
    """
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """None

    """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful.

        :return:
        """
        payload = {
            "email": "test@travelperk.com",
            "password": "password123",
            "name": "Test Name"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(status.HTTP_201_CREATED, res.status_code)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_duplicate_user(self):
        """Test creating user that already exists fails.

        :return:
        """
        payload = {
            "email": "test@travelperk.com",
            "password": "password123",
            "name": "Test Name"
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_password_too_short(self):
        """Test that the password must be long enough.

        :return:
        """
        payload = {
            "email": "test@travelperk.com",
            "password": "pw",
            "name": "Test Name"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

        user_exists = get_user_model().objects.filter(
            email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user.

        :return:
        """
        payload = {
            "email": "test@travelperk.com",
            "password": "testpass"
        }

        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEquals(status.HTTP_200_OK, res.status_code)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created if invalid credentials are given.

        :return:
        """
        create_user(email="test@travelperk.com", password="testpass")

        payload = {
            "email": "test@travelperk.com",
            "password": "wrongg"
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_create_token_no_user(self):
        """Test that a token is not created if user doesn't exist.

        :return:
        """
        payload = {
            "email": "test@travelperk.com",
            "password": "wrongg"
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_create_token_missing_field(self):
        """Test that email and password are required.

        :return:
        """
        res = self.client.post(TOKEN_URL, {
            "email": "one",
            "password": ""
        })
        self.assertNotIn("token", res.data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_retrieve_user_unauthorized(self):
        """Test that user cannot be retrieved if not authorized

        :return:
        """
        res = self.client.get(ME_URL)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)


class PrivateUserAPITests(TestCase):
    """Test API requests that require authentication

    """

    def setUp(self) -> None:
        self.user = create_user(
            email="test@travelperk.com",
            password="password123",
            name="Test User"
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user

        :return:
        """
        res = self.client.get(ME_URL)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual({
            "name": self.user.name,
            "email": self.user.email
        }, res.data)

    def test_post_me_not_allowed(self):
        """Test cannot post to me url

        :return:
        """
        res = self.client.post(ME_URL, {})
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, res.status_code)

    def test_update_user_profile(self):
        """Test update profile

        :return:
        """
        payload = {
            "name": "New Test User",
            "password": "newpassword123"
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(payload['name'], self.user.name)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(status.HTTP_200_OK, res.status_code)
