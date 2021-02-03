from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """None

    """

    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@travelperk.com", password="password123")
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@travelperk.com", password="password123",
            name="Riaan Swart")

    def test_users_listed(self):
        """Users are listed on user page

        :return:
        """
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test user change page

        :return:
        """
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(200, res.status_code)

    def test_user_add_page(self):
        """Test user create page

        :return:
        """
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
