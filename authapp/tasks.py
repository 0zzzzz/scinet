from django.conf import settings
from django.core.mail import send_mail, mail_admins
from django.urls import reverse
from celery import shared_task


@shared_task
def send_verify_email(email_user, activate_key):
    verify_link = reverse('auth:verify', args=[email_user, activate_key])
    full_link = f'{settings.DOMAIN_NAME}{verify_link}'
    message = f'Ссылка для активации вашей учетной записи:  {full_link}'

    send_mail('Account activation', activate_key, settings.EMAIL_HOST_USER, [email_user])

    return send_mail(
        f'Активация аккаунта на сайте {settings.DOMAIN_NAME}',
        message,
        settings.EMAIL_HOST_USER,
        [email_user],
        fail_silently=False
    )
