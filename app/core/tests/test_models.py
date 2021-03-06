from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@travelperk.com", password="password123"):
    """

    :param email:
    :param password:
    :return:
    """
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_string(self):
        """

        :return:
        """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan"
        )

        self.assertEqual(tag.name, str(tag))

    def test_ingredient_str(self):
        """

        :return:
        """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )

        self.assertEquals(ingredient.name, str(ingredient))

    def test_recipe_str(self):
        """

        :return:
        """
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Steak & Mushroom Sauce",
            time_minutes=5,
            price=5.00

        )

        self.assertEquals(recipe.title, str(recipe))

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test that image is saved in correct location

        :return:
        """
        uuid = "test_uuid"
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(None, "my_image.jpg")

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(exp_path, file_path)
