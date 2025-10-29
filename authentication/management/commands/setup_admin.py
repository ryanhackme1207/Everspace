from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create a superuser for admin access'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superuser', default='ryanadmin')
        parser.add_argument('--email', type=str, help='Email for the superuser', default='admin@everspace.com')
        parser.add_argument('--password', type=str, help='Password for the superuser', default='ryanadmin12345')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            # Delete existing user if exists to ensure clean creation
            if User.objects.filter(username=username).exists():
                User.objects.filter(username=username).delete()
                self.stdout.write(
                    self.style.WARNING(f'Deleted existing user "{username}"')
                )

            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser "{username}"')
            )
            self.stdout.write(f'  Username: {username}')
            self.stdout.write(f'  Email: {email}')
            self.stdout.write(f'  Password: {password}')
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS('You can now access the admin interface at:')
            )
            self.stdout.write('  http://127.0.0.1:8000/admin/')
            self.stdout.write('')
            self.stdout.write(
                'IMPORTANT: Change the default password after first login!'
            )
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )