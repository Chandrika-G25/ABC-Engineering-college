from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Department, Course, AcademicYear, Semester, StudentProfile, TeacherProfile, Subject, Attendance, TeacherAttendance, ExamMark, StudentFee
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds complete B.Tech Engineering SMS database for all 4 Academic Years (I, II, III, IV Year)'

    def handle(self, *args, **kwargs):
        # 1. Single Admin User (admin@gmail.com / admin123)
        admin_u, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@gmail.com', 'role': User.ROLE_SUPER_ADMIN, 'first_name': 'Super', 'last_name': 'Admin', 'is_superuser': True, 'is_staff': True}
        )
        admin_u.email = 'admin@gmail.com'
        admin_u.set_password('admin123')
        admin_u.save()

        # 2. B.Tech Branches / Departments
        branches_data = [
            {'code': 'CIVIL', 'name': 'Civil Engineering', 'description': 'B.Tech Department of Civil Engineering'},
            {'code': 'EEE', 'name': 'Electrical & Electronics Engineering', 'description': 'B.Tech Department of Electrical & Electronics'},
            {'code': 'ECE', 'name': 'Electronics & Communication Engineering', 'description': 'B.Tech Department of Electronics & Communication'},
            {'code': 'CSE', 'name': 'Computer Science & Engineering', 'description': 'B.Tech Department of Computer Science & Engineering'},
            {'code': 'IT', 'name': 'Information Technology', 'description': 'B.Tech Department of Information Technology'},
            {'code': 'AIDS', 'name': 'Artificial Intelligence & Data Science', 'description': 'B.Tech Department of AI & Data Science'},
        ]

        created_branches = {}
        created_courses = {}
        for b in branches_data:
            dept, _ = Department.objects.get_or_create(code=b['code'], defaults=b)
            created_branches[b['code']] = dept
            
            c, _ = Course.objects.get_or_create(
                code=f"BTECH-{b['code']}",
                defaults={
                    'name': f"B.Tech {b['name']}",
                    'department': dept,
                    'duration_years': 4
                }
            )
            created_courses[b['code']] = c

        # 3. Academic Year & Semester
        ay, _ = AcademicYear.objects.get_or_create(name='2026-2027', defaults={'start_date': date(2026, 7, 1), 'end_date': date(2027, 6, 30), 'is_current': True})
        sem1, _ = Semester.objects.get_or_create(academic_year=ay, semester_number=1, defaults={'name': 'Semester 1', 'start_date': date(2026, 7, 1), 'end_date': date(2026, 12, 15), 'is_current': True})

        # 4. Teachers for Branches
        teachers_info = [
            ('T101', 'Prof. John Doe', 'john.doe@university.edu', created_branches['CSE'], 'Professor & HoD'),
            ('T102', 'Dr. Sarah Smith', 'sarah.smith@university.edu', created_branches['ECE'], 'Associate Professor'),
            ('T103', 'Prof. Robert Vance', 'robert.vance@university.edu', created_branches['AIDS'], 'Assistant Professor'),
            ('T104', 'Dr. Michael Chang', 'michael.c@university.edu', created_branches['EEE'], 'Associate Professor'),
            ('T105', 'Prof. David Wilson', 'david.w@university.edu', created_branches['CIVIL'], 'Professor'),
            ('T106', 'Dr. Emily Watson', 'emily.w@university.edu', created_branches['IT'], 'Assistant Professor'),
        ]

        created_teachers = []
        for tid, name, email, dept, desig in teachers_info:
            u, _ = User.objects.get_or_create(username=tid.lower(), defaults={'email': email, 'role': User.ROLE_TEACHER, 'first_name': name})
            u.set_password('Password123!')
            u.save()

            tp, _ = TeacherProfile.objects.get_or_create(
                teacher_id=tid,
                defaults={'user': u, 'full_name': name, 'email': email, 'phone': '+919876543210', 'department': dept, 'designation': desig}
            )
            created_teachers.append(tp)

        # 5. Students across ALL 4 Academic Years (I, II, III, IV Year) and ALL 6 Departments
        # Batch Prefixes by Academic Year:
        # I Year (1st Year): 25691A... (Starting 2 numbers are 25 for ALL 1st year students)
        # II Year (2nd Year): 24691A...
        # III Year (3rd Year): 23691A...
        # IV Year (4th Year): 22691A...
        students_info = [
            # ================= I YEAR (1st Year - Prefix: 25691A...) =================
            ('25691A0401', 'ADM20250401', 'Gundla Madugu Chandrika', 'chandrikag2005@gmail.com', created_branches['ECE'], 'Female', 'I'),
            ('25691A0402', 'ADM20250402', 'Rajesh Kumar', 'rajesh.ece@student.edu', created_branches['ECE'], 'Male', 'I'),
            ('25691A0403', 'ADM20250403', 'Suresh Babu', 'suresh.ece@student.edu', created_branches['ECE'], 'Male', 'I'),

            ('25691A0501', 'ADM20250501', 'Rahul Varma', 'rahul.v@student.edu', created_branches['CSE'], 'Male', 'I'),
            ('25691A0502', 'ADM20250502', 'Ananya Roy', 'ananya.cse@student.edu', created_branches['CSE'], 'Female', 'I'),
            ('25691A0503', 'ADM20250503', 'Manish Reddy', 'manish.cse@student.edu', created_branches['CSE'], 'Male', 'I'),

            ('25691A1201', 'ADM20251201', 'Sneha Patel', 'sneha.it@student.edu', created_branches['IT'], 'Female', 'I'),
            ('25691A1202', 'ADM20251202', 'Vikram Singh', 'vikram.it@student.edu', created_branches['IT'], 'Male', 'I'),

            ('25691A0201', 'ADM20250201', 'Karthik Reddy', 'karthik.eee@student.edu', created_branches['EEE'], 'Male', 'I'),
            ('25691A0202', 'ADM20250202', 'Pooja Naidu', 'pooja.eee@student.edu', created_branches['EEE'], 'Female', 'I'),

            ('25691A0101', 'ADM20250101', 'Mahesh Babu', 'mahesh.civil@student.edu', created_branches['CIVIL'], 'Male', 'I'),
            ('25691A0102', 'ADM20250102', 'Divya Sharma', 'divya.civil@student.edu', created_branches['CIVIL'], 'Female', 'I'),

            ('25691A6601', 'ADM20256601', 'Priya Sharma', 'priya.s@student.edu', created_branches['AIDS'], 'Female', 'I'),
            ('25691A6602', 'ADM20256602', 'Arjun Mehta', 'arjun.aids@student.edu', created_branches['AIDS'], 'Male', 'I'),

            # ================= II YEAR (2nd Year - Prefix: 24691A...) =================
            ('24691A0401', 'ADM20240401', 'Nikhil Teja', 'nikhil.ece2@student.edu', created_branches['ECE'], 'Male', 'II'),
            ('24691A0402', 'ADM20240402', 'Bhavana Rao', 'bhavana.ece2@student.edu', created_branches['ECE'], 'Female', 'II'),

            ('24691A0501', 'ADM20240501', 'Sai Kumar', 'sai.cse2@student.edu', created_branches['CSE'], 'Male', 'II'),
            ('24691A0502', 'ADM20240502', 'Keerthi Reddy', 'keerthi.cse2@student.edu', created_branches['CSE'], 'Female', 'II'),

            ('24691A1201', 'ADM20241201', 'Harsha Vardhan', 'harsha.it2@student.edu', created_branches['IT'], 'Male', 'II'),
            ('24691A1202', 'ADM20241202', 'Meghana K', 'meghana.it2@student.edu', created_branches['IT'], 'Female', 'II'),

            ('24691A0201', 'ADM20240201', 'Venkatesh M', 'venkatesh.eee2@student.edu', created_branches['EEE'], 'Male', 'II'),
            ('24691A0202', 'ADM20240202', 'Swathi P', 'swathi.eee2@student.edu', created_branches['EEE'], 'Female', 'II'),

            ('24691A0101', 'ADM20240101', 'Tarun Kumar', 'tarun.civil2@student.edu', created_branches['CIVIL'], 'Male', 'II'),
            ('24691A0102', 'ADM20240102', 'Shruti Verma', 'shruti.civil2@student.edu', created_branches['CIVIL'], 'Female', 'II'),

            ('24691A6601', 'ADM20246601', 'Kiran Roy', 'kiran.aids2@student.edu', created_branches['AIDS'], 'Male', 'II'),
            ('24691A6602', 'ADM20246602', 'Navya Shree', 'navya.aids2@student.edu', created_branches['AIDS'], 'Female', 'II'),

            # ================= III YEAR (3rd Year - Prefix: 23691A...) =================
            ('23691A0401', 'ADM20230401', 'Pavan Kalyan', 'pavan.ece3@student.edu', created_branches['ECE'], 'Male', 'III'),
            ('23691A0402', 'ADM20230402', 'Sirisha K', 'sirisha.ece3@student.edu', created_branches['ECE'], 'Female', 'III'),

            ('23691A0501', 'ADM20230501', 'Gautham Krishna', 'gautham.cse3@student.edu', created_branches['CSE'], 'Male', 'III'),
            ('23691A0502', 'ADM20230502', 'Lavanya M', 'lavanya.cse3@student.edu', created_branches['CSE'], 'Female', 'III'),

            ('23691A1201', 'ADM20231201', 'Deepak Chawla', 'deepak.it3@student.edu', created_branches['IT'], 'Male', 'III'),
            ('23691A1202', 'ADM20231202', 'Ritu Sen', 'ritu.it3@student.edu', created_branches['IT'], 'Female', 'III'),

            ('23691A0201', 'ADM20230201', 'Srikanth N', 'srikanth.eee3@student.edu', created_branches['EEE'], 'Male', 'III'),
            ('23691A0202', 'ADM20230202', 'Vandana R', 'vandana.eee3@student.edu', created_branches['EEE'], 'Female', 'III'),

            ('23691A0101', 'ADM20230101', 'Rakesh Sharma', 'rakesh.civil3@student.edu', created_branches['CIVIL'], 'Male', 'III'),
            ('23691A0102', 'ADM20230102', 'Deepika P', 'deepika.civil3@student.edu', created_branches['CIVIL'], 'Female', 'III'),

            ('23691A6601', 'ADM20236601', 'Abhinav Gupta', 'abhinav.aids3@student.edu', created_branches['AIDS'], 'Male', 'III'),
            ('23691A6602', 'ADM20236602', 'Preeti Singh', 'preeti.aids3@student.edu', created_branches['AIDS'], 'Female', 'III'),

            # ================= IV YEAR (4th Year - Prefix: 22691A...) =================
            ('22691A0401', 'ADM20220401', 'Vijay Kumar', 'vijay.ece4@student.edu', created_branches['ECE'], 'Male', 'IV'),
            ('22691A0402', 'ADM20220402', 'Madhavi Latha', 'madhavi.ece4@student.edu', created_branches['ECE'], 'Female', 'IV'),

            ('22691A0501', 'ADM20220501', 'Aditya Varma', 'aditya.cse4@student.edu', created_branches['CSE'], 'Male', 'IV'),
            ('22691A0502', 'ADM20220502', 'Ramya Krishna', 'ramya.cse4@student.edu', created_branches['CSE'], 'Female', 'IV'),

            ('22691A1201', 'ADM20221201', 'Varun Tej', 'varun.it4@student.edu', created_branches['IT'], 'Male', 'IV'),
            ('22691A1202', 'ADM20221202', 'Soundarya R', 'soundarya.it4@student.edu', created_branches['IT'], 'Female', 'IV'),

            ('22691A0201', 'ADM20220201', 'Prakash Rao', 'prakash.eee4@student.edu', created_branches['EEE'], 'Male', 'IV'),
            ('22691A0202', 'ADM20220202', 'Archana G', 'archana.eee4@student.edu', created_branches['EEE'], 'Female', 'IV'),

            ('22691A0101', 'ADM20220101', 'Naveen Kumar', 'naveen.civil4@student.edu', created_branches['CIVIL'], 'Male', 'IV'),
            ('22691A0102', 'ADM20220102', 'Bhavya Sree', 'bhavya.civil4@student.edu', created_branches['CIVIL'], 'Female', 'IV'),

            ('22691A6601', 'ADM20226601', 'Rohan Sharma', 'rohan.aids4@student.edu', created_branches['AIDS'], 'Male', 'IV'),
            ('22691A6602', 'ADM20226602', 'Tanya Malhotra', 'tanya.aids4@student.edu', created_branches['AIDS'], 'Female', 'IV'),
        ]

        created_students = []
        for sid, adm, name, email, dept, gender, yr in students_info:
            u, _ = User.objects.get_or_create(username=sid.lower(), defaults={'email': email, 'role': User.ROLE_STUDENT, 'first_name': name})
            u.set_password('Password123!')
            u.save()

            course = Course.objects.filter(department=dept).first()

            sp, created = StudentProfile.objects.get_or_create(
                student_id=sid,
                defaults={
                    'user': u,
                    'admission_number': adm,
                    'full_name': name,
                    'email': email,
                    'phone': '+918125815674',
                    'address': 'University Campus Hostel',
                    'department': dept,
                    'course': course,
                    'academic_year': ay,
                    'year': yr,
                    'gender': gender,
                    'status': 'Active'
                }
            )
            if not created:
                sp.department = dept
                sp.course = course
                sp.full_name = name
                sp.email = email
                sp.year = yr
                sp.status = 'Active'
                sp.save()
            created_students.append(sp)

        # 6. Department-Specific Subjects
        subjects_data = [
            # ECE Subjects
            ('EC401', 'Digital Signal Processing', created_courses['ECE'], created_teachers[1]),
            ('EC402', 'VLSI Design & Technology', created_courses['ECE'], created_teachers[1]),
            ('EC403', 'Microprocessors & Microcontrollers', created_courses['ECE'], created_teachers[1]),
            ('EC404', 'Communication Systems', created_courses['ECE'], created_teachers[1]),

            # CSE Subjects
            ('CS501', 'Data Structures & Algorithms', created_courses['CSE'], created_teachers[0]),
            ('CS502', 'Database Management Systems', created_courses['CSE'], created_teachers[0]),
            ('CS503', 'Operating Systems', created_courses['CSE'], created_teachers[0]),
            ('CS504', 'Computer Networks & Security', created_courses['CSE'], created_teachers[0]),

            # IT Subjects
            ('IT1201', 'Cloud Computing & Virtualization', created_courses['IT'], created_teachers[5]),
            ('IT1202', 'Information & Cyber Security', created_courses['IT'], created_teachers[5]),
            ('IT1203', 'Web Architecture & Frameworks', created_courses['IT'], created_teachers[5]),

            # EEE Subjects
            ('EE201', 'Power Electronics & Drives', created_courses['EEE'], created_teachers[3]),
            ('EE202', 'Electrical Power Systems & Grid', created_courses['EEE'], created_teachers[3]),
            ('EE203', 'Control Systems & Automation', created_courses['EEE'], created_teachers[3]),

            # CIVIL Subjects
            ('CE101', 'Structural Analysis & Design', created_courses['CIVIL'], created_teachers[4]),
            ('CE102', 'Concrete Technology & Structures', created_courses['CIVIL'], created_teachers[4]),
            ('CE103', 'Soil Mechanics & Geotechnical Engg', created_courses['CIVIL'], created_teachers[4]),

            # AIDS Subjects
            ('AD6601', 'Artificial Intelligence Principles', created_courses['AIDS'], created_teachers[2]),
            ('AD6602', 'Machine Learning Algorithms', created_courses['AIDS'], created_teachers[2]),
            ('AD6603', 'Deep Learning & Neural Networks', created_courses['AIDS'], created_teachers[2]),
        ]

        created_subjects = []
        for code, sub_name, course, teacher in subjects_data:
            sub, _ = Subject.objects.get_or_create(
                code=code,
                defaults={'name': sub_name, 'course': course, 'semester': sem1, 'assigned_teacher': teacher}
            )
            created_subjects.append(sub)

        # 7. Student Attendance Records across ALL students
        for sp in created_students:
            matching_sub = Subject.objects.filter(course=sp.course).first()
            if matching_sub:
                Attendance.objects.get_or_create(student=sp, subject=matching_sub, attendance_date=date.today(), defaults={'status': 'Present'})

        # 8. Teacher Attendance Records
        for tp in created_teachers:
            TeacherAttendance.objects.get_or_create(teacher=tp, attendance_date=date.today(), defaults={'status': 'Present'})

        # 9. Exam Marks across Sem I & Sem II
        from core.curriculum import CURRICULUM_DATA, get_default_mark_for_student
        for sp in created_students:
            dept_code = sp.department.code if sp.department else 'ECE'
            yr = sp.year or 'I'
            for sem in ['Sem I', 'Sem II']:
                subs = CURRICULUM_DATA.get(dept_code, {}).get(yr, {}).get(sem, [])
                for sub in subs:
                    score = get_default_mark_for_student(sp.student_id, sub['code'], sem)
                    ExamMark.objects.update_or_create(
                        student=sp,
                        semester=sem,
                        subject_code=sub['code'],
                        defaults={
                            'subject': sub['name'],
                            'exam_name': f'{sem} Final Examination',
                            'marks_obtained': score,
                            'total_marks': 100.00
                        }
                    )

        # 10. Student Fees Invoices across students
        for idx, sp in enumerate(created_students):
            paid = 55000.00 if idx % 2 == 0 else 25000.00
            StudentFee.objects.get_or_create(
                student=sp,
                title=f'Semester 1 {sp.department.code} Tuition Fee',
                defaults={
                    'user_account': sp.user,
                    'fee_type': StudentFee.FEE_TYPE_TUITION,
                    'course': sp.course,
                    'academic_year': ay,
                    'total_amount': 55000.00,
                    'paid_amount': paid,
                    'payment_method': 'Online / UPI',
                    'due_date': date.today() + timedelta(days=15)
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded B.Tech SMS Database with all 4 Academic Years (I, II, III, IV Year), 1st Year batch prefix 25691A..., department subjects, teachers, attendance, and fee records!'))
