# Generated by Django 4.0.4 on 2022-06-07 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0002_remove_snuserprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='snuserprofile',
            name='gender',
            field=models.CharField(choices=[('M', 'Мужской'), ('W', 'Женский'), ('O', 'Иное')], default='O', max_length=1, verbose_name='Пол'),
        ),
    ]
