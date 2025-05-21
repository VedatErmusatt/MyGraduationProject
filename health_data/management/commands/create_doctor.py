from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a doctor user and adds them to the Doctors group"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Doctor email")
        parser.add_argument("password", type=str, help="Doctor password")
        parser.add_argument("--first-name", type=str, help="Doctor first name", default="")
        parser.add_argument("--last-name", type=str, help="Doctor last name", default="")
        parser.add_argument("--username", type=str, help="Doctor username", default=None)

    def handle(self, *args, **options):
        # Get or create Doctors group
        doctors_group, created = Group.objects.get_or_create(name="Doktorlar")

        # Create doctor user
        email = options["email"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]
        username = options["username"] or email.split("@")[0]  # Use email prefix as username if not provided

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User with email {email} already exists"))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User with username {username} already exists"))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        # Add user to Doctors group
        user.groups.add(doctors_group)

        self.stdout.write(self.style.SUCCESS(f"Successfully created doctor user: {user.get_full_name() or user.email}"))
