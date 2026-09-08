from django.core.management.base import BaseCommand
from core.models import Department, Course, AcademicYear, Semester
from datetime import date

class Command(BaseCommand):
    help = 'Seeds initial real-world Academic data (Departments, Courses, Academic Years, Semesters)'

    def handle(self, *args, **kwargs):
        # 1. Departments
        depts_data = [
            {'code': 'CSE', 'name': 'Computer Science & Engineering', 'description': 'Department of CS & Software Engineering'},
            {'code': 'IT', 'name': 'Information Technology', 'description': 'Department of IT & Cloud Systems'},
            {'code': 'ECE', 'name': 'Electronics & Communication', 'description': 'Department of Electronics & Embedded Hardware'},
            {'code': 'MECH', 'name': 'Mechanical Engineering', 'description': 'Department of Thermal & Mechanical Systems'},
            {'code': 'CIVIL', 'name': 'Civil Engineering', 'description': 'Department of Structural & Infrastructure Engineering'},
        ]

        created_depts = {}
        for d in depts_data:
            dept, _ = Department.objects.get_or_create(code=d['code'], defaults=d)
            created_depts[d['code']] = dept

        # 2. Courses
        courses_data = [
            {'code': 'BTECH-CSE', 'name': 'B.Tech Computer Science & Engineering', 'department': created_depts['CSE'], 'duration_years': 4},
            {'code': 'BCA', 'name': 'Bachelor of Computer Applications', 'department': created_depts['IT'], 'duration_years': 3},
            {'code': 'MCA', 'name': 'Master of Computer Applications', 'department': created_depts['IT'], 'duration_years': 2},
            {'code': 'BTECH-ECE', 'name': 'B.Tech Electronics & Communication', 'department': created_depts['ECE'], 'duration_years': 4},
            {'code': 'BTECH-MECH', 'name': 'B.Tech Mechanical Engineering', 'department': created_depts['MECH'], 'duration_years': 4},
        ]

        for c in courses_data:
            Course.objects.get_or_create(code=c['code'], defaults=c)

        # 3. Academic Year
        ay, _ = AcademicYear.objects.get_or_create(
            name='2026-2027',
            defaults={
                'start_date': date(2026, 7, 1),
                'end_date': date(2027, 6, 30),
                'is_current': True
            }
        )

        # 4. Semesters
        Semester.objects.get_or_create(
            academic_year=ay,
            semester_number=1,
            defaults={
                'name': 'Semester 1',
                'start_date': date(2026, 7, 1),
                'end_date': date(2026, 12, 15),
                'is_current': True
            }
        )
        Semester.objects.get_or_create(
            academic_year=ay,
            semester_number=2,
            defaults={
                'name': 'Semester 2',
                'start_date': date(2027, 1, 5),
                'end_date': date(2027, 5, 30),
                'is_current': False
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Academic data (Departments, Courses, Academic Year 2026-2027, Semesters)!'))
