from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User Model extending Django's AbstractUser.
    Supports Role-Based Access Control (RBAC) across 4 roles:
    - SUPER_ADMIN
    - ADMIN
    - TEACHER
    - STUDENT
    """
    ROLE_SUPER_ADMIN = 'SUPER_ADMIN'
    ROLE_ADMIN = 'ADMIN'
    ROLE_TEACHER = 'TEACHER'
    ROLE_STUDENT = 'STUDENT'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Admin'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_STUDENT, 'Student'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
        help_text="Designates the access control role of the user."
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPER_ADMIN or self.is_superuser

    @property
    def is_admin_user(self):
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN] or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def get_role_badge_class(self):
        badges = {
            self.ROLE_SUPER_ADMIN: 'bg-purple-100 text-purple-800',
            self.ROLE_ADMIN: 'bg-blue-100 text-blue-800',
            self.ROLE_TEACHER: 'bg-green-100 text-green-800',
            self.ROLE_STUDENT: 'bg-yellow-100 text-yellow-800',
        }
        return badges.get(self.role, 'bg-gray-100 text-gray-800')
