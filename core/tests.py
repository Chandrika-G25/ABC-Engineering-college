from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from core.models import Department, Course, AcademicYear, Semester, StudentProfile, StudentFee

User = get_user_model()

class AcademicModelTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            code='CSE',
            name='Computer Science'
        )
        self.course = Course.objects.create(
            code='BTECH-CSE',
            name='B.Tech CSE',
            department=self.dept,
            duration_years=4
        )
        self.user = User.objects.create_user(
            username='fee_student',
            password='Password123!',
            role=User.ROLE_STUDENT
        )
        self.student = StudentProfile.objects.create(
            user=self.user,
            student_id='22691A2843',
            admission_number='ADM2026001',
            full_name='Test Student',
            email='test@student.com',
            course=self.course
        )

    def test_department_creation(self):
        self.assertEqual(str(self.dept), 'Computer Science (CSE)')
        self.assertTrue(self.dept.is_active)

    def test_course_relationship(self):
        self.assertEqual(self.course.department.code, 'CSE')
        self.assertEqual(self.dept.courses.count(), 1)

    def test_academic_year_single_current(self):
        ay1 = AcademicYear.objects.create(
            name='2025-2026',
            start_date=date(2025, 7, 1),
            end_date=date(2026, 6, 30),
            is_current=True
        )
        self.assertTrue(ay1.is_current)

        ay2 = AcademicYear.objects.create(
            name='2026-2027',
            start_date=date(2026, 7, 1),
            end_date=date(2027, 6, 30),
            is_current=True
        )
        ay1.refresh_from_db()
        self.assertFalse(ay1.is_current)
        self.assertTrue(ay2.is_current)

    def test_student_fee_status_and_remaining_due(self):
        fee = StudentFee.objects.create(
            student=self.student,
            title='Tuition Fee Test',
            total_amount=10000.00,
            paid_amount=4000.00,
            due_date=date.today() + timedelta(days=10)
        )
        self.assertEqual(fee.remaining_due, 6000.00)
        self.assertEqual(fee.status, StudentFee.STATUS_PARTIAL)

        # Full Payment Update
        fee.paid_amount = 10000.00
        fee.save()
        self.assertEqual(fee.status, StudentFee.STATUS_PAID)
        self.assertEqual(fee.remaining_due, 0.00)
