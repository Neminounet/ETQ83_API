from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Urls de test :
# ================


def delete_url_function(user):
    return reverse("user:user-delete",
                   kwargs={"pk": user.id})


CREATE_USER_URL = reverse("user:user-create")
LOGIN_URL = reverse("user:user-login")
LIST_URL = reverse("user:user-list")
ME_URL = reverse("user:user-update")
PASSWORD_UPDATE_URL = reverse("user:user-update-password")
LOGOUT_URL = reverse("user:user-logout")


def create_user(**params):
    return get_user_model().objects.create_user(**params)

# Test publics (User non authentifié):
# =========================================
# Les méthodes doivent commencer par test


class PublicUserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_sucess(self):
        payload = {
            "email": "gerard@gmail.com",
            "first_name": "Gérard",
            "last_name": "Michaud",
            "password": "Gerard123"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_user_email_exists(self):
        payload = {
            "email": "gerard@gmail.com",
            "first_name": "Gérard",
            "last_name": "Michaud",
            "password": "Gerard123"
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        payload = {
            "email": "gerard@gmail.com",
            "first_name": "Gérard",
            "last_name": "Michaud",
            "password": "Ger"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_login_token_sucess(self):
        payload = {
            "email": "gerard@gmail.com",
            "first_name": "Gérard",
            "last_name": "Michaud",
            "password": "Gerard123"
        }
        create_user(**payload)

        payload2 = {
            "email": payload["email"],
            "password": payload["password"],
        }
        res = self.client.post(LOGIN_URL, payload2)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_token_bad_credentials(self):
        payload = {
            "email": "gerard@gmail.com",
            "first_name": "Gérard",
            "last_name": "Michaud",
            "password": "Gerard123"
        }
        create_user(**payload)
        payload2 = {
            "email": payload["email"],
            "password": "blabla",
        }

        res = self.client.post(LOGIN_URL, payload2)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_my_profile_error(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_profiles_error(self):
        res = self.client.get(LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

 # Test privés (User authentifié):
# =========================================


class PrivateUserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="gerard@gmail.com", first_name="Gérard", last_name="Michaud", password="Gerard123")
        self.client.force_authenticate(user=self.user)

    def test_get_my_profile_sucess(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_profile(self):
        payload = {"first_name": "Jean-Gérard", "last_name": "Delavega"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_password(self):
        payload = {"password": "Password123"}
        res = self.client.put(PASSWORD_UPDATE_URL, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_all_profile_error(self):
        res = self.client.get(LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_user_error(self):
        payload = {
            "email": "doudou@gmail.com",
            "first_name": "Gérard",
            "last_name": "Michaud",
            "password": "Gerard123"
        }

        created_user = create_user(**payload)
        delete_url = delete_url_function(created_user)
        res = self.client.delete(delete_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        user_exists = get_user_model().objects.filter(
            email=payload["email"]).exists()
        self.assertTrue(user_exists)

# Pour le superuser uniquement.
# ============================


class SuperUserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(email="francis@gmail.com",
                                                                    first_name="Francis", last_name="Dupont", password="Francis123")
        self.client.force_authenticate(user=self.admin_user)

    def test_user_delete_user_success(self):
        payload = {
            "email": "gerard@gmail.com",
            "first_name": "Gérard",
            "last_name": "Michaud",
            "password": "Gerard123"
        }

        created_user = create_user(**payload)
        delete_url = delete_url_function(created_user)
        res = self.client.delete(delete_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(id=created_user.id)

    def test_get_all_profile_success(self):
        res = self.client.get(LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
