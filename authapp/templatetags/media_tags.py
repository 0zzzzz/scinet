from django.conf import settings
from django import template

from authapp.models import SNUser

register = template.Library()


@register.filter(name='media_for_users')
def media_for_users(img_path):
    if not img_path:
        img_path = 'users_avatars/default.jpg'
    return f'{settings.MEDIA_URL}{img_path}'


@register.filter(name='index_empty')
def index_empty(img_path):
    if not img_path:
        img_path = 'technical_img/default.jpg'
    return f'{img_path}'


@register.simple_tag
def get_companion(user, chat):
    for u in chat.members.all():
        if u != user:
            return u
    return None
