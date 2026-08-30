from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from .models import ContactMessage
from .views import ContactMessageCreateView


@patch.object(ContactMessageCreateView, "throttle_classes", [])
class ContactMessageAPITests(APITestCase):
    url = "/api/contact/"

    valid_payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "subject": "Project Inquiry",
        "message": "I would like to discuss a project with you.",
    }

    def test_valid_contact_submission(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)

        contact = ContactMessage.objects.first()

        self.assertEqual(contact.name, "John Doe")
        self.assertEqual(contact.email, "john@example.com")
        self.assertEqual(contact.subject, "Project Inquiry")
        self.assertEqual(
            contact.message,
            "I would like to discuss a project with you.",
        )
        self.assertIsNotNone(contact.ip_address)
        self.assertFalse(contact.email_sent)

    def test_missing_name_is_rejected(self):
        payload = self.valid_payload.copy()
        payload.pop("name")

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["email"] = "not-an-email"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_empty_message_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["message"] = "   "

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_oversized_message_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["message"] = "a" * 5001

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_ip_address_cannot_be_submitted_by_client(self):
        payload = self.valid_payload.copy()
        payload["ip_address"] = "8.8.8.8"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contact = ContactMessage.objects.first()

        self.assertNotEqual(contact.ip_address, "8.8.8.8")
        self.assertIsNotNone(contact.ip_address)

    def test_email_sent_cannot_be_set_by_client(self):
        payload = self.valid_payload.copy()
        payload["email_sent"] = True

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contact = ContactMessage.objects.first()

        self.assertFalse(contact.email_sent)

    def test_get_is_not_allowed(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

from django.core.cache import cache

class ContactMessageThrottleTests(APITestCase):
    url = "/api/contact/"

    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "subject": "Testing throttle",
        "message": "This is a throttle test.",
    }

    def setUp(self):
        cache.clear()

    def test_contact_endpoint_is_throttled(self):
        for _ in range(5):
            response = self.client.post(
                self.url,
                self.payload,
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
            )

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )