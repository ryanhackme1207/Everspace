from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create superuser for production deployment'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='ryanadmin', help='Username for superuser')
        parser.add_argument('--email', type=str, default='admin@everspace.com', help='Email for superuser')
        parser.add_argument('--password', type=str, default='ryanadmin12345', help='Password for superuser')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists. Updating password...')
                )
                user = User.objects.get(username=username)
                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated superuser "{username}"')
                )
            else:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser "{username}"')
                )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )