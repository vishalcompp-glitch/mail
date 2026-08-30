import logging
import os

from rest_framework import generics, status
from rest_framework.response import Response

from .models import ContactMessage
from .serializers import ContactMessageSerializer
from .services import send_contact_email
from .throttles import ContactMessageThrottle


logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Render terminates TLS at its proxy/load balancer and forwards
    requests to the Django service.

    In production on Render, use the first IP from X-Forwarded-For.
    Locally, fall back to REMOTE_ADDR.
    """
    if os.getenv("RENDER"):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    throttle_classes = [ContactMessageThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact = serializer.save(
            ip_address=get_client_ip(request)
        )

        try:
            send_contact_email(contact)

        except Exception:
            logger.exception(
                "Failed to send contact email. contact_id=%s",
                contact.id,
            )

            contact.email_error = "Email delivery failed."
            contact.save(update_fields=["email_error"])

            return Response(
                {
                    "detail": (
                        "Your message was received, "
                        "but email delivery failed."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        contact.email_sent = True
        contact.save(update_fields=["email_sent"])

        return Response(
            {
                "detail": "Your message has been sent successfully."
            },
            status=status.HTTP_201_CREATED,
        )