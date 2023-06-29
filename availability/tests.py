from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from availability.models import Availability, RendezVous, Message
import datetime

# Constantes :
# ======================

AVAILABILITY_URL = reverse("availability:availability-list")
AVAILABILITY_URL_SU = reverse("availability:superuser-availability-list")
RDV_URL = reverse("availability:rendezvous-list")
MESSAGE_URL = reverse("availability:messages-list")


def detail_avail_url(avail_id):
    return reverse("availability:superuser-availability-detail", args=[avail_id])


def detail_rdv_url(rdv_id):
    return reverse("availability:rendezvous-detail", args=[rdv_id])


def detail_msg_url(msg_id):
    return reverse("availability:messages-detail", args=[msg_id])

# Fonction de création :
# ==================================


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_availability(**params):
    payload = {
        "date": datetime.date.today(),
        "heure": datetime.time(10, 0),
        "is_taken": False
    }
    payload.update(params)
    return Availability.objects.create(**payload)


def create_rendezvous(user, avail):
    payload = {
        "user": user,
        "degree": "CP",
        "availability": avail
    }
    return RendezVous.objects.create(**payload)


def create_message(rdv, sender, **params):
    payload = {
        "content": "Ceci est un message de test",
        "date_time": "2023-07-01 12:00"
    }
    payload.update(params)
    return Message.objects.create(rdv=rdv, sender=sender, **payload)


class AvailabilityModelTests_SU(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="gerard@gmail.com", first_name="Gérard", last_name="Michaud", password="Gerard123")
        self.availability = create_availability()
        self.client.force_authenticate(user=self.user)

    def test_create_availability_success(self):
        payload = {
            "date": datetime.date.today(),
            "heure": datetime.time(12, 0),
            "is_taken": False
        }
        res = self.client.post(AVAILABILITY_URL_SU, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        avail_exists = Availability.objects.filter(**payload).exists()
        self.assertTrue(avail_exists)

    def test_get_detail_availability(self):
        availability_id = self.availability.id
        detail_url = detail_avail_url(availability_id)
        res = self.client.get(detail_url)
        self.assertEqual(self.availability.id, res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_availability(self):
        availability_id = self.availability.id
        delete_url = detail_avail_url(availability_id)
        res = self.client.delete(delete_url)
        with self.assertRaises(Availability.DoesNotExist):
            Availability.objects.get(id=availability_id)


class RendezVousModelTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="gerard@gmail.com", first_name="Gérard", last_name="Michaud", password="Gerard123")
        self.avail = create_availability()
        self.client.force_authenticate(user=self.user)

    def test_create_rdv_success(self):
        payload = {
            "user": self.user.id,
            "degree": "CE1",
            "availability": self.avail.id,
        }
        res = self.client.post(RDV_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        rdv_exists = RendezVous.objects.filter(
            user=payload["user"], degree=payload["degree"], availability=payload["availability"]).exists()
        self.assertTrue(rdv_exists)

    def test_get_detail_rdv(self):
        rendezvous = create_rendezvous(self.user, self.avail)
        rendezvous_id = rendezvous.id
        detail_url = detail_rdv_url(rendezvous_id)
        res = self.client.get(detail_url)
        self.assertEqual(rendezvous.id, res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_rendezvous(self):
        rendezvous = create_rendezvous(self.user, self.avail)
        rendezvous_id = rendezvous.id
        delete_url = detail_rdv_url(rendezvous_id)
        res = self.client.delete(delete_url)
        with self.assertRaises(RendezVous.DoesNotExist):
            RendezVous.objects.get(id=rendezvous_id)


class MessageModelTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="gerard@gmail.com", first_name="Gérard", last_name="Michaud", password="Gerard123")
        self.avail = create_availability()
        self.client.force_authenticate(user=self.user)

    def test_create_message_api(self):
        rendezvous = create_rendezvous(self.user, self.avail)
        payload = {
            "content": "Ceci est un message de test",
            "date_time": "2023-07-01 13:00",
            "rdv": rendezvous.id,
            "sender": self.user.id,
        }
        res = self.client.post(MESSAGE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['content'], payload['content'])
        self.assertEqual(res.data['rdv'], payload['rdv'])
        self.assertEqual(res.data['sender']["id"], payload['sender'])

    def test_get_detail_message_api(self):
        rendezvous = create_rendezvous(self.user, self.avail)
        message = create_message(rendezvous, self.user)
        detail_url = detail_msg_url(message.id)
        res = self.client.get(detail_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], message.id)

    def test_delete_message_api(self):
        rendezvous = create_rendezvous(self.user, self.avail)
        message = create_message(rendezvous, self.user)
        detail_url = detail_msg_url(message.id)
        res = self.client.delete(detail_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=message.id)
