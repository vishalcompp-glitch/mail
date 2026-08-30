from rest_framework import generics

from .models import ContactMessage
from .serializers import ContactMessageSerializer
from .services import send_contact_email
from .throttles import ContactMessageThrottle


class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    throttle_classes = [ContactMessageThrottle]

    def perform_create(self, serializer):
        contact = serializer.save(
            ip_address=self.request.META.get("REMOTE_ADDR")
        )

        try:
            send_contact_email(contact)
        except Exception as exc:
            contact.email_error = str(exc)
            contact.save(update_fields=["email_error"])

            raise

        contact.email_sent = True
        contact.save(update_fields=["email_sent"])