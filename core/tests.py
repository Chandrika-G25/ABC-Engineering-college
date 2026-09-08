from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date
from core.models import Department, Course, AcademicYear, Semester

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

    def test_semester_date_validation(self):
        ay = AcademicYear.objects.create(
            name='2026-2027',
            start_date=date(2026, 7, 1),
            end_date=date(2027, 6, 30)
        )
        invalid_sem = Semester(
            academic_year=ay,
            semester_number=1,
            name='Sem 1',
            start_date=date(2026, 12, 1),
            end_date=date(2026, 6, 1)  # Invalid: end date before start date
        )
        with self.assertRaises(ValidationError):
            invalid_sem.full_clean()
