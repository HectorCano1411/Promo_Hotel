from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message_text, recipient_email):
    send_mail(
        subject,
        message_text,
        settings.EMAIL_HOST_USER,  # Dirección del remitente
        [recipient_email],  # Destinatario
        fail_silently=False,
    )
