from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserModelTests(TestCase):
    def setUp(self):
        self.super_admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Password123!',
            role=User.ROLE_SUPER_ADMIN,
            is_superuser=True
        )
        self.teacher = User.objects.create_user(
            username='teacher_test',
            email='teacher@test.com',
            password='Password123!',
            role=User.ROLE_TEACHER
        )
        self.student = User.objects.create_user(
            username='student_test',
            email='student@test.com',
            password='Password123!',
            role=User.ROLE_STUDENT
        )

    def test_user_role_properties(self):
        self.assertTrue(self.super_admin.is_super_admin)
        self.assertTrue(self.super_admin.is_admin_user)
        self.assertFalse(self.super_admin.is_teacher)

        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.teacher.is_admin_user)

        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_teacher)

    def test_password_hashing(self):
        self.assertTrue(self.student.check_password('Password123!'))
        self.assertFalse(self.student.check_password('WrongPassword'))


class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='Password123!',
            role=User.ROLE_STUDENT
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'johndoe',
            'password': 'Password123!'
        })
        self.assertRedirects(response, reverse('core:home'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_failure(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'johndoe',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout(self):
        self.client.login(username='johndoe', password='Password123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertFalse('_auth_user_id' in self.client.session)
