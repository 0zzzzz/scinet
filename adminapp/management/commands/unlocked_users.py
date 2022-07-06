from django.core.management import BaseCommand
from django.utils import timezone
from authapp.models import SNUser

today = timezone.now()


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = SNUser.objects.filter(date_blocked_end__lte=today)

        if users:
            for user in users:
                print(user)
                user.unlocked_user()

            self.stdout.write("Unlocked")
        else:
            self.stdout.write("No users")
