from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """None

    """

    def test_create_user_with_email(self):
        """Test creating a new user with an email

        :return:
        """
        email = "test@travelperk.com"
        password = "testpass123"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """Test the email for a new user is normalised

        :return:
        """
        email = "user@TRavelPERk.COM"
        user = get_user_model().objects.create_user(
            email=email,
            password='test123'
        )

        self.assertEqual(email.lower(), user.email)

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error

        :return:
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='test123'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser

        :return:
        """
        user = get_user_model().objects.create_superuser(
            email="admin@travelperk.com",
            password="testpass123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)