from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Department, Course, AcademicYear, Semester, StudentProfile, TeacherProfile, Subject, Attendance, ExamMark, StudentFee
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds complete real-world university dataset matching SMS ERP reference system'

    def handle(self, *args, **kwargs):
        # 1. Users
        admin_u, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@gmail.com', 'role': User.ROLE_SUPER_ADMIN, 'first_name': 'Super', 'last_name': 'Admin', 'is_superuser': True, 'is_staff': True}
        )
        admin_u.set_password('admin123')
        admin_u.save()

        teacher_u, _ = User.objects.get_or_create(
            username='prof_john',
            defaults={'email': 'john.doe@university.edu', 'role': User.ROLE_TEACHER, 'first_name': 'John', 'last_name': 'Doe'}
        )
        teacher_u.set_password('Password123!')
        teacher_u.save()

        student_u, _ = User.objects.get_or_create(
            username='student_alex',
            defaults={'email': 'chandrikag2005@gmail.com', 'role': User.ROLE_STUDENT, 'first_name': 'Gundla', 'last_name': 'Chandrika'}
        )
        student_u.set_password('Password123!')
        student_u.save()

        # 2. Departments
        cse_dept, _ = Department.objects.get_or_create(code='CSE', defaults={'name': 'Computer Science & Engineering', 'description': 'Department of CS & Software'})
        it_dept, _ = Department.objects.get_or_create(code='IT', defaults={'name': 'Information Technology', 'description': 'Department of IT & Cloud'})
        ece_dept, _ = Department.objects.get_or_create(code='ECE', defaults={'name': 'Electronics & Communication', 'description': 'Department of Electronics'})

        # 3. Courses
        btech_cse, _ = Course.objects.get_or_create(code='BTECH-CSE', defaults={'name': 'B.Tech Computer Science & Engineering', 'department': cse_dept, 'duration_years': 4})
        bca, _ = Course.objects.get_or_create(code='BCA', defaults={'name': 'Bachelor of Computer Applications', 'department': it_dept, 'duration_years': 3})

        # 4. Academic Year & Semester
        ay, _ = AcademicYear.objects.get_or_create(name='2026-2027', defaults={'start_date': date(2026, 7, 1), 'end_date': date(2027, 6, 30), 'is_current': True})
        sem1, _ = Semester.objects.get_or_create(academic_year=ay, semester_number=1, defaults={'name': 'Semester 1', 'start_date': date(2026, 7, 1), 'end_date': date(2026, 12, 15), 'is_current': True})

        # 5. Teacher Profile
        t_profile, _ = TeacherProfile.objects.get_or_create(
            teacher_id='T101',
            defaults={
                'user': teacher_u,
                'full_name': 'Prof. John Doe',
                'email': 'john.doe@university.edu',
                'phone': '+919876543210',
                'department': cse_dept,
                'designation': 'Senior Professor'
            }
        )

        # 6. Student Profile
        sp, _ = StudentProfile.objects.get_or_create(
            student_id='22691A2843',
            defaults={
                'user': student_u,
                'admission_number': 'ADM2026001',
                'full_name': 'Gundla Madugu Chandrika',
                'email': 'chandrikag2005@gmail.com',
                'phone': '+918125815674',
                'address': 'Peddakotla village, Tadimarri Mandal, Sri Satya Sai District',
                'department': cse_dept,
                'course': btech_cse,
                'academic_year': ay,
                'gender': 'Female',
                'status': 'Active'
            }
        )

        # 7. Subjects
        sub1, _ = Subject.objects.get_or_create(code='CS101', defaults={'name': 'Data Structures & Algorithms', 'course': btech_cse, 'semester': sem1, 'assigned_teacher': t_profile})
        sub2, _ = Subject.objects.get_or_create(code='CS102', defaults={'name': 'Database Management Systems', 'course': btech_cse, 'semester': sem1, 'assigned_teacher': t_profile})

        # 8. Attendance Records
        Attendance.objects.get_or_create(student=sp, subject=sub1, attendance_date=date.today(), defaults={'status': 'Present'})
        Attendance.objects.get_or_create(student=sp, subject=sub2, attendance_date=date.today(), defaults={'status': 'Present'})

        # 9. Examination Marks
        ExamMark.objects.get_or_create(student=sp, exam_name='Mid-term Examination', subject='Data Structures & Algorithms', defaults={'marks_obtained': 88.50, 'total_marks': 100.00})
        ExamMark.objects.get_or_create(student=sp, exam_name='Mid-term Examination', subject='Database Systems', defaults={'marks_obtained': 92.00, 'total_marks': 100.00})

        # 10. Student Fees
        StudentFee.objects.get_or_create(
            student=sp,
            title='Semester 1 Tuition Fee',
            defaults={
                'user_account': student_u,
                'fee_type': StudentFee.FEE_TYPE_TUITION,
                'course': btech_cse,
                'academic_year': ay,
                'total_amount': 45000.00,
                'paid_amount': 25000.00,
                'payment_method': 'Online / UPI',
                'due_date': date.today() + timedelta(days=15)
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded complete SMS ERP database! (Users, Profiles, Subjects, Attendance, Marks, Fees)'))
