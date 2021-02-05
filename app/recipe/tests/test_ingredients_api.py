from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class TestPublicIngredientsAPI(TestCase):
    """Public tests for ingredients API

    """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """

        :return:
        """
        res = self.client.get(INGREDIENTS_URL)

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

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients

        :return:
        """
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(serializer.data, res.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the authenticated user

        :return:
        """
        other_user = get_user_model().objects.create_user(
            email="test2@travelperk.com",
            password="password123",
            name="Test User 2"
        )

        ingredient = Ingredient.objects.create(user=self.user, name="Vinegar")
        Ingredient.objects.create(user=other_user, name="Turmeric")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEquals(1, len(res.data))
        self.assertEquals(ingredient.name, res.data[0]['name'])
