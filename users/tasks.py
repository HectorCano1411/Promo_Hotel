
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task
from django.urls import reverse
import logging
logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(subject, message_text, email, token):
    verification_link = f"{settings.FRONTEND_URL}{reverse('verify_email', kwargs={'token': token})}"
    message = f'{message_text} {verification_link}'

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f'Error al enviar el correo a {email}: {e}')
