from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


class TestPublicTagsAPI(TestCase):
    """Public tests for tags API

    """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """

        :return:
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)


class TestPrivateTagsAPI(TestCase):
    """Private tetss for tags API

    """

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="test@travelperk.com",
            password="password123",
            name="Test User"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags

        :return:
        """
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(serializer.data, res.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user

        :return:
        """
        other_user = get_user_model().objects.create_user(
            email="test2@travelperk.com",
            password="password123",
            name="Test User 2"
        )

        tag = Tag.objects.create(user=self.user, name="Comfort Food")
        Tag.objects.create(user=other_user, name="Fruity")

        res = self.client.get(TAGS_URL)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEquals(1, len(res.data))
        self.assertEquals(tag.name, res.data[0]['name'])
