from rest_framework.test import APIClient, APITestCase
from rest_framework import status, permissions
from .models import User, UserProfile


class UserTest(APITestCase):
    fixtures = ["users.json"]
    registration_endpoint = "/accounts/register/"
    dashboard_endpoint = "/accounts/dashboard/"
    endpoint = "/accounts/users/"

    def setUp(self):
        self.client = APIClient()
        self.super_admin = User.objects.create_user(
            email="superadmin@gmail.com",
            password="asdf",
            is_superuser=True,
            first_name="Super",
            last_name="Mario"
        )
        self.piu = User.objects.create_user(
            email="piu@gmail.com",
            password="asdf",
            is_superuser=False,
            first_name="PIU",
            last_name="Mario"
        )

    def super_admin_login(self):
        UserProfile.objects.get_or_create(user=self.super_admin)
        self.client.force_authenticate(user=self.super_admin)

    def regular_user_login(self):
        UserProfile.objects.get_or_create(user=self.piu)
        self.client.force_authenticate(user=self.piu)

    def test_registration(self):
        data = {
            "email": "superadmin2@gmail.com",
            "first_name": "Super",
            "last_name": "Admin",
            "password": "asdf"
        }

        response = self.client.post(
            self.registration_endpoint,
            data=data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(permissions.AllowAny().has_permission(response,None), True)
        self.assertEqual(data["email"], response.data.get("email"))

    def test_super_admin_get_all_users_on_platform(self):
        self.super_admin_login()
        new_user = User.objects.create(
            email="new-user@gmail.com",
            password="asdf",
            first_name="Fis",
        )
        response = self.client.get(self.dashboard_endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), User.objects.all().count())

    def test_registration_with_no_data_fails(self):
        response = self.client.post(
            self.registration_endpoint,
            data={},
            format="json"
        )

        self.assertEqual(permissions.AllowAny().has_permission(response,None), True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_existing_email_fails(self):
        data = {
            "email": "superadmin@gmail.com",
            "first_name": "Super",
            "last_name": "Admin",
            "password": "asdf"
        }

        response = self.client.post(
            self.registration_endpoint,
            data=data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(permissions.AllowAny().has_permission(response,None), True)

    def test_user_can_update_own_data(self):
        data = {
            "first_name": "Cow and Chicken",
            "last_name": "Disney Junior"
        }
        self.regular_user_login()
        url = f"{self.dashboard_endpoint}{self.piu.id}/"
        response = self.client.patch(
            url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_update_others_data(self):
        data = {
            "first_name": "Cow and Chicken",
            "last_name": "Disney Junior"
        }
        self.regular_user_login()
        url = f"{self.dashboard_endpoint}{self.super_admin.id}/"
        response = self.client.patch(
            url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_super_admin_can_update_user_succeeds(self):
        data = {
            "first_name": "Cow and Chicken",
            "last_name": "Disney Junior"
        }
        self.super_admin_login()
        url = f"{self.dashboard_endpoint}{self.super_admin.id}/"
        response = self.client.patch(
            url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_super_admin_can_delete_user_succeeds(self):
        new_user = User.objects.create(
            email="new-user@gmail.com",
            password="asdf",
            first_name="John"
        )
        self.super_admin_login()
        url = f"{self.dashboard_endpoint}{new_user.id}/"
        response = self.client.delete(
            url, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 5)

    def test_user_can_delete_own_account(self):
        self.regular_user_login()
        url = f"{self.dashboard_endpoint}{self.piu.id}/"
        response = self.client.delete(
            url, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 4)

    def test_user_cannot_delete_other_user_accounts(self):
        new_user = User.objects.create(
            email="new-user@gmail.com",
            password="asdf",
            first_name="John"
        )
        self.regular_user_login()
        url = f"{self.dashboard_endpoint}{new_user.id}/"
        response = self.client.delete(
            url, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(User.objects.all().count(), 6)
        self.assertNotEqual(User.objects.all().count(), 5)

    def test_resend_reset_password_email(self):
        data = {"email": "piu@gmail.com"}
        response = self.client.post(
            "/accounts/password-reset/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_get_own_profile(self):
        response = self.client.get(self.dashboard_endpoint)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
