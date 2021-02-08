from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Return recipe detail URL

    :param recipe_id:
    :return:
    """
    return reverse("recipe:recipe-detail", args=[recipe_id])


def sample_tag(user, name="Main Course"):
    """Create and return a sample tag

    :param user:
    :param name:
    :return:
    """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Cinnamon"):
    """Create and return a sample ingredient

    :param user:
    :param name:
    :return:
    """
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test view recipe detail

        :return:
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(serializer.data, res.data)

    def test_create_basic_recipe(self):
        """Test creating recipe

        :return:
        """
        payload = {
            "title": "Cheesecake",
            "time_minutes": 30,
            "price": 5.00
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEquals(value, getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags

        :return:
        """
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")

        payload = {
            "title": "Avocado Lime Cheesecake",
            "tags": [tag1.id, tag2.id],
            "time_minutes": 60,
            "price": 20.00
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)

        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(2, recipe.tags.count())
        self.assertIn(tag1, recipe.tags.all())
        self.assertIn(tag2, recipe.tags.all())

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients

        :return:
        """
        ingredient1 = sample_ingredient(user=self.user, name="Prawns")
        ingredient2 = sample_ingredient(user=self.user, name="Ginger")

        payload = {
            "title": "Thai Prawn Red Curry",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 20,
            "price": 7.00
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)

        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(2, recipe.ingredients.count())
        self.assertIn(ingredient1, recipe.ingredients.all())
        self.assertIn(ingredient2, recipe.ingredients.all())

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch

        :return:
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(self.user))

        new_tag = sample_tag(user=self.user, name="Curries")
        payload = {
            "title": "Chicken Tikka",
            "tags": [new_tag.id]
        }
        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])

        tags = recipe.tags.all()
        self.assertEquals(1, len(tags))
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put

        :return:
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(self.user))

        payload = {
            "title": "Spaghetti Carbonara",
            "time_minutes": 25,
            "price": 5.0
        }
        url = detail_url(recipe.id)

        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(payload['title'], recipe.title)
        self.assertEqual(payload['time_minutes'], recipe.time_minutes)
        self.assertEqual(payload['price'], recipe.price)

        tags = recipe.tags.all()
        self.assertEquals(0, len(tags))
