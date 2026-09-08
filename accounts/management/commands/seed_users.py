from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Seeds default initial users for each system role (SUPER_ADMIN, ADMIN, TEACHER, STUDENT)'

    def handle(self, *args, **kwargs):
        seed_users = [
            {
                'username': 'admin',
                'email': 'admin@university.edu',
                'password': 'Password123!',
                'role': User.ROLE_SUPER_ADMIN,
                'first_name': 'Super',
                'last_name': 'Admin',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'college_admin',
                'email': 'sysadmin@university.edu',
                'password': 'Password123!',
                'role': User.ROLE_ADMIN,
                'first_name': 'System',
                'last_name': 'Admin',
                'is_superuser': False,
                'is_staff': True,
            },
            {
                'username': 'prof_john',
                'email': 'john.doe@university.edu',
                'password': 'Password123!',
                'role': User.ROLE_TEACHER,
                'first_name': 'John',
                'last_name': 'Doe',
                'is_superuser': False,
                'is_staff': False,
            },
            {
                'username': 'student_alex',
                'email': 'alex.smith@student.university.edu',
                'password': 'Password123!',
                'role': User.ROLE_STUDENT,
                'first_name': 'Alex',
                'last_name': 'Smith',
                'is_superuser': False,
                'is_staff': False,
            },
        ]

        for user_data in seed_users:
            pwd = user_data.pop('password')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            user.set_password(pwd)
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()

            status = "CREATED" if created else "UPDATED"
            self.stdout.write(self.style.SUCCESS(f'User "{user.username}" [{user.role}] successfully {status}.'))
