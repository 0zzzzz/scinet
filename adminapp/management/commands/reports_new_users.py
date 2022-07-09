from datetime import timedelta, time, datetime
from django.core.mail import mail_admins
from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware
from authapp.models import SNUser

today = timezone.now()
tomorrow = today + timedelta(days=1)
today_start = make_aware(datetime.combine(today, time()))
today_end = make_aware(datetime.combine(tomorrow, time()))


class Command(BaseCommand):
    subject = (
        f"Отчет о новых пользователях с {today_start.strftime('%d-%m-%Y')} "
        f"по {today_end.strftime('%d-%m-%Y')}"
    )

    def handle(self, *args, **options):
        new_users = SNUser.objects.filter(date_joined__range=(today_start, today_end))

        if new_users:
            message = f"{self.subject}\n"

            for user in new_users:
                message += f'Пользователь {user}\n'

            mail_admins(subject=self.subject, message=message, html_message=None)
