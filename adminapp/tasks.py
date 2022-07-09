from django.core.management import call_command
from celery import shared_task


@shared_task
def send_email_report_new_users():
    call_command("reports_new_users", )


@shared_task
def send_email_report_new_posts():
    call_command("reports_new_posts", )


@shared_task
def task_unlocked_users():
    call_command("unlocked_users", )
