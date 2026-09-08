from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum, Q, Count
from django.contrib.auth import get_user_model
from datetime import datetime, date
from accounts.decorators import admin_required, teacher_required
from .models import Department, Course, AcademicYear, Semester, StudentProfile, TeacherProfile, Subject, Attendance, ExamMark, StudentFee
from .forms import (
    DepartmentForm, CourseForm, AcademicYearForm, SemesterForm,
    StudentProfileForm, TeacherProfileForm, SubjectForm, AttendanceRecordForm,
    ExamMarkForm, StudentFeeForm, RecordPaymentForm
)

User = get_user_model()

def home_view(request):
    """
    SMS ERP System Control Dashboard with real-time metrics and quick management.
    """
    students_count = StudentProfile.objects.filter(status='Active').count()
    teachers_count = TeacherProfile.objects.filter(status='Active').count()
    attendance_count = Attendance.objects.count()
    marks_count = ExamMark.objects.count()
    dept_count = Department.objects.filter(is_active=True).count()
    course_count = Course.objects.filter(is_active=True).count()

    current_year = AcademicYear.objects.filter(is_current=True).first()
    current_sem = Semester.objects.filter(is_current=True).first()

    # Fee metrics calculation
    fee_aggregates = StudentFee.objects.aggregate(
        total=Sum('total_amount'),
        paid=Sum('paid_amount')
    )
    total_fee_billed = fee_aggregates['total'] or 0.00
    total_fee_collected = fee_aggregates['paid'] or 0.00
    total_fee_pending = total_fee_billed - total_fee_collected

    recent_students = StudentProfile.objects.all().order_by('-created_at')[:6]
    recent_attendance = Attendance.objects.select_related('student', 'subject').order_by('-created_at')[:5]

    context = {
        'db_name': settings.DATABASES['default']['NAME'],
        'students_count': students_count,
        'teachers_count': teachers_count,
        'attendance_count': attendance_count,
        'marks_count': marks_count,
        'dept_count': dept_count,
        'course_count': course_count,
        'current_year': current_year,
        'current_sem': current_sem,
        'total_fee_billed': total_fee_billed,
        'total_fee_collected': total_fee_collected,
        'total_fee_pending': total_fee_pending,
        'recent_students': recent_students,
        'recent_attendance': recent_attendance,
        'courses': Course.objects.filter(is_active=True),
        'departments': Department.objects.filter(is_active=True),
    }
    return render(request, 'home.html', context)


# ==========================================
# STUDENT MANAGEMENT VIEWS
# ==========================================

@login_required
def student_list_view(request):
    students = StudentProfile.objects.all().select_related('course', 'department')
    search_query = request.GET.get('search', '')
    course_id = request.GET.get('course', '')

    if search_query:
        students = students.filter(
            Q(full_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    if course_id:
        students = students.filter(course_id=course_id)

    if request.method == 'POST' and request.user.is_admin_user:
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            st = form.save()
            messages.success(request, f"Student '{st.full_name}' ({st.student_id}) enrolled successfully!")
            return redirect('core:student_list')
        else:
            messages.error(request, "Error enrolling student. Please check form errors.")
    else:
        form = StudentProfileForm()

    return render(request, 'core/students/student_list.html', {
        'students': students,
        'form': form,
        'search_query': search_query,
        'selected_course': course_id,
        'courses': Course.objects.filter(is_active=True)
    })


@admin_required
def student_create_view(request):
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            st = form.save()
            messages.success(request, f"Student '{st.full_name}' created successfully!")
            return redirect('core:student_list')
    else:
        form = StudentProfileForm()
    return render(request, 'core/students/student_form.html', {'form': form, 'title': 'Register New Student'})


@admin_required
def student_edit_view(request, pk):
    st = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=st)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{st.full_name}' updated successfully.")
            return redirect('core:student_list')
    else:
        form = StudentProfileForm(instance=st)
    return render(request, 'core/students/student_form.html', {'form': form, 'title': f"Edit Student - {st.student_id}", 'student': st})


@admin_required
def student_delete_view(request, pk):
    st = get_object_or_404(StudentProfile, pk=pk)
    st_name = st.full_name
    st.delete()
    messages.success(request, f"Student '{st_name}' deleted successfully.")
    return redirect('core:student_list')


# ==========================================
# TEACHER MANAGEMENT VIEWS
# ==========================================

@login_required
def teacher_list_view(request):
    teachers = TeacherProfile.objects.all().select_related('department')
    if request.method == 'POST' and request.user.is_admin_user:
        form = TeacherProfileForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Teacher '{t.full_name}' added successfully!")
            return redirect('core:teacher_list')
    else:
        form = TeacherProfileForm()

    return render(request, 'core/teachers/teacher_list.html', {
        'teachers': teachers,
        'form': form
    })


# ==========================================
# SUBJECT MANAGEMENT VIEWS
# ==========================================

@login_required
def subject_list_view(request):
    subjects = Subject.objects.all().select_related('course', 'semester', 'assigned_teacher')
    if request.method == 'POST' and request.user.is_admin_user:
        form = SubjectForm(request.POST)
        if form.is_valid():
            sub = form.save()
            messages.success(request, f"Subject '{sub.name}' ({sub.code}) added successfully!")
            return redirect('core:subject_list')
    else:
        form = SubjectForm()

    return render(request, 'core/subjects/subject_list.html', {
        'subjects': subjects,
        'form': form
    })


# ==========================================
# ATTENDANCE MANAGEMENT VIEWS
# ==========================================

@login_required
def attendance_list_view(request):
    records = Attendance.objects.all().select_related('student', 'subject')
    students = StudentProfile.objects.filter(status='Active')
    subjects = Subject.objects.all()

    if request.method == 'POST':
        form = AttendanceRecordForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.recorded_by = request.user
            att.save()
            messages.success(request, f"Attendance marked '{att.status}' for {att.student.full_name}.")
            return redirect('core:attendance_list')
        else:
            messages.error(request, "Error saving attendance record.")
    else:
        form = AttendanceRecordForm(initial={'attendance_date': date.today()})

    return render(request, 'core/attendance/attendance_list.html', {
        'records': records,
        'students': students,
        'subjects': subjects,
        'form': form
    })


# ==========================================
# MARKS & EXAMINATIONS MANAGEMENT VIEWS
# ==========================================

@login_required
def marks_list_view(request):
    marks = ExamMark.objects.all().select_related('student')
    students = StudentProfile.objects.filter(status='Active')

    if request.method == 'POST':
        form = ExamMarkForm(request.POST)
        if form.is_valid():
            m = form.save()
            messages.success(request, f"Marks saved for {m.student.full_name} ({m.marks_obtained}/{m.total_marks}).")
            return redirect('core:marks_list')
        else:
            messages.error(request, "Error saving examination marks.")
    else:
        form = ExamMarkForm()

    return render(request, 'core/marks/marks_list.html', {
        'marks': marks,
        'students': students,
        'form': form
    })


# ==========================================
# DEPARTMENT & COURSE CRUD VIEWS
# ==========================================

@login_required
def department_list_view(request):
    departments = Department.objects.all().select_related('head_of_department')
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(name__icontains=search_query) | departments.filter(code__icontains=search_query)
    
    return render(request, 'core/departments/department_list.html', {
        'departments': departments,
        'search_query': search_query
    })


@admin_required
def department_create_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' ({dept.code}) created successfully!")
            return redirect('core:department_list')
    else:
        form = DepartmentForm()

    return render(request, 'core/departments/department_form.html', {'form': form, 'title': 'Add New Department'})


@admin_required
def department_edit_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{dept.name}' updated successfully.")
            return redirect('core:department_list')
    else:
        form = DepartmentForm(instance=dept)

    return render(request, 'core/departments/department_form.html', {'form': form, 'title': f"Edit Department - {dept.code}", 'department': dept})


@login_required
def course_list_view(request):
    courses = Course.objects.all().select_related('department')
    search_query = request.GET.get('search', '')
    dept_id = request.GET.get('department', '')

    if search_query:
        courses = courses.filter(name__icontains=search_query) | courses.filter(code__icontains=search_query)
    if dept_id:
        courses = courses.filter(department_id=dept_id)

    return render(request, 'core/courses/course_list.html', {
        'courses': courses,
        'departments': Department.objects.filter(is_active=True),
        'search_query': search_query,
        'selected_dept': dept_id
    })


@admin_required
def course_create_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.name}' created successfully!")
            return redirect('core:course_list')
    else:
        form = CourseForm()
    return render(request, 'core/courses/course_form.html', {'form': form, 'title': 'Add New Course'})


@admin_required
def course_edit_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.name}' updated successfully.")
            return redirect('core:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'core/courses/course_form.html', {'form': form, 'title': f"Edit Course - {course.code}", 'course': course})


@login_required
def academic_year_list_view(request):
    years = AcademicYear.objects.all()
    if request.method == 'POST':
        form = AcademicYearForm(request.POST)
        if form.is_valid():
            yr = form.save()
            messages.success(request, f"Academic Year '{yr.name}' saved successfully.")
            return redirect('core:academic_year_list')
    else:
        form = AcademicYearForm()
    return render(request, 'core/academic/academic_years.html', {'years': years, 'form': form})


@login_required
def semester_list_view(request):
    semesters = Semester.objects.all().select_related('academic_year')
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            sem = form.save()
            messages.success(request, f"Semester '{sem.name}' saved successfully.")
            return redirect('core:semester_list')
    else:
        form = SemesterForm()
    return render(request, 'core/academic/semesters.html', {'semesters': semesters, 'form': form})


# ==========================================
# FEE MANAGEMENT VIEWS
# ==========================================

@login_required
def fee_list_view(request):
    fees = StudentFee.objects.all().select_related('student', 'course', 'academic_year')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        fees = fees.filter(
            Q(student__student_id__icontains=search_query) |
            Q(student__full_name__icontains=search_query) |
            Q(title__icontains=search_query)
        )
    if status_filter:
        fees = fees.filter(status=status_filter)

    fee_aggregates = fees.aggregate(
        total=Sum('total_amount'),
        paid=Sum('paid_amount')
    )
    total_billed = fee_aggregates['total'] or 0.00
    total_paid = fee_aggregates['paid'] or 0.00
    total_due = total_billed - total_paid

    students = StudentProfile.objects.filter(status='Active')

    return render(request, 'core/fees/fee_list.html', {
        'fees': fees,
        'students': students,
        'search_query': search_query,
        'selected_status': status_filter,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_due': total_due,
        'status_choices': StudentFee.STATUS_CHOICES,
    })


@admin_required
def fee_create_view(request):
    if request.method == 'POST':
        form = StudentFeeForm(request.POST)
        if form.is_valid():
            fee = form.save()
            messages.success(request, f"Fee invoice '{fee.title}' issued successfully!")
            return redirect('core:fee_list')
        else:
            messages.error(request, "Error creating fee invoice.")
    else:
        form = StudentFeeForm()

    return render(request, 'core/fees/fee_form.html', {'form': form, 'title': 'Create Student Fee Invoice'})


@admin_required
def fee_pay_view(request, pk):
    fee = get_object_or_404(StudentFee, pk=pk)
    if request.method == 'POST':
        form = RecordPaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['payment_amount']
            method = form.cleaned_data['payment_method']
            fee.paid_amount += amount
            fee.payment_method = method
            fee.payment_date = datetime.now()
            fee.save()
            messages.success(request, f"Payment of ₹{amount} recorded via {method}. New status: {fee.get_status_display()}.")
            return redirect('core:fee_list')
    else:
        form = RecordPaymentForm(initial={'payment_amount': fee.remaining_due})

    return render(request, 'core/fees/record_payment.html', {'fee': fee, 'form': form})


# ==========================================
# REPORTS VIEW (Module 21)
# ==========================================

@login_required
def reports_view(request):
    students = StudentProfile.objects.all().select_related('course', 'department')
    teachers = TeacherProfile.objects.all().select_related('department')
    attendance = Attendance.objects.all().select_related('student', 'subject')
    marks = ExamMark.objects.all().select_related('student')
    fees = StudentFee.objects.all().select_related('student')

    dept_stats = Department.objects.annotate(student_count=Count('studentprofile')).filter(is_active=True)
    course_stats = Course.objects.annotate(student_count=Count('studentprofile')).filter(is_active=True)

    return render(request, 'core/reports/reports.html', {
        'students_count': students.count(),
        'teachers_count': teachers.count(),
        'dept_stats': dept_stats,
        'course_stats': course_stats,
        'recent_students': students.order_by('-created_at')[:10],
        'recent_marks': marks[:10],
        'recent_fees': fees[:10],
    })
