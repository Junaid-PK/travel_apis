from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserPoints


class Command(BaseCommand):
    help = 'Initialize UserPoints for all existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0
        existing_count = 0

        for user in users:
            points, created = UserPoints.objects.get_or_create(user=user)
            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {users.count()} users. '
                f'Created {created_count} new UserPoints, '
                f'{existing_count} already existed.'
            )
        )
