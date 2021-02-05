from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    """Create and return sample recipe

    :param user:
    :param params:
    :return:
    """
    defaults = {
        "title": "Sample Recipe",
        "time_minutes": 10,
        "price": 5.00
    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class TestPublicRecipeAPI(TestCase):
    """Public tests for recipes API

    """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """

        :return:
        """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)


class TestPrivateTagsAPI(TestCase):
    """Private tests for tags API

    """

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="test@travelperk.com",
            password="password123",
            name="Test User"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving recipes

        :return:
        """
        sample_recipe(self.user, title="Bolognaise")
        sample_recipe(self.user, title="Carbonara")

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-title")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(serializer.data, res.data)

    def test_recipes_limited_to_user(self):
        """Test that recipes returned are for the authenticated user

        :return:
        """
        other_user = get_user_model().objects.create_user(
            email="test2@travelperk.com",
            password="password123",
            name="Test User 2"
        )

        sample_recipe(user=self.user, title="Bolognaise")
        sample_recipe(user=other_user, title="Carbonara")

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEquals(1, len(res.data))
        self.assertEqual(serializer.data, res.data)
