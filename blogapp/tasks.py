from django.core.mail import mail_admins

from celery import shared_task


@shared_task
def new_comment_moderator_notification(from_user_cel, text_cel, to_user_cel):
    subject = "Новый комментарий пользователя"
    message = f"Пользователь {from_user_cel} оставил следующий комментарий '{text_cel}' к посту пользователя " \
              f"{to_user_cel}. Его нужно проверить!"
    print(from_user_cel)
    print(text_cel)
    print(to_user_cel)
    mail_admins(subject=subject, message=message, html_message=None)

