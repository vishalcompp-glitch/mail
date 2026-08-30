import os

import resend

from .models import ContactMessage


def send_contact_email(contact: ContactMessage) -> str:
    api_key = os.getenv("RESEND_API_KEY")
    email_from = os.getenv("EMAIL_FROM")
    contact_email = os.getenv("CONTACT_EMAIL")

    if not api_key:
        raise RuntimeError("RESEND_API_KEY is not configured.")

    if not email_from:
        raise RuntimeError("EMAIL_FROM is not configured.")

    if not contact_email:
        raise RuntimeError("CONTACT_EMAIL is not configured.")

    resend.api_key = api_key

    response = resend.Emails.send(
        {
            "from": email_from,
            "to": [contact_email],
            "reply_to": contact.email,
            "subject": contact.subject,
            "text": (
                f"Name: {contact.name}\n"
                f"Email: {contact.email}\n"
                f"IP Address: {contact.ip_address}\n\n"
                f"Message:\n{contact.message}"
            ),
        }
    )

    return response["id"]