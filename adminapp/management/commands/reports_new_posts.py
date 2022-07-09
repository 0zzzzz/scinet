from datetime import timedelta, time, datetime
from django.core.mail import mail_admins, send_mail
from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware
from blogapp.models import SNPosts

today = timezone.now()
tomorrow = today + timedelta(days=1)
today_start = make_aware(datetime.combine(today, time()))
today_end = make_aware(datetime.combine(tomorrow, time()))


class Command(BaseCommand):
    subject = (
        f"Отчет о новых постах с {today_start.strftime('%d-%m-%Y')} по {today_end.strftime('%d-%m-%Y')}"
    )

    def handle(self, *args, **options):
        new_posts = SNPosts.objects.filter(created_at__range=(today_start, today_end))

        if new_posts:
            message = f"{self.subject}\n"

            for post in new_posts:
                message += f'Пост {post}\n'

            mail_admins(subject=self.subject, message=message, html_message=None)

        else:
            message = "Новых постов нет"

        mail_admins(subject=self.subject, message=message, html_message=None)
