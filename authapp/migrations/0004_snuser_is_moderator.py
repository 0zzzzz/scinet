# Generated by Django 4.0.3 on 2022-06-21 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0003_snuserprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='snuser',
            name='is_moderator',
            field=models.BooleanField(default=False, verbose_name='Модератор'),
        ),
    ]
