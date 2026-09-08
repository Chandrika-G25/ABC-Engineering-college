from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum, Q, Count
from django.contrib.auth import get_user_model
from datetime import datetime, date
from accounts.decorators import admin_required
from .models import Department, Course, AcademicYear, Semester, StudentFee
from .forms import DepartmentForm, CourseForm, AcademicYearForm, SemesterForm, StudentFeeForm, RecordPaymentForm

User = get_user_model()

def home_view(request):
    """
    Renders the enhanced central system overview dashboard with live metrics, fee collection statistics, and status checks.
    """
    students_count = User.objects.filter(role=User.ROLE_STUDENT).count()
    teachers_count = User.objects.filter(role=User.ROLE_TEACHER).count()
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
    overdue_count = StudentFee.objects.filter(status=StudentFee.STATUS_OVERDUE).count()

    # Recent activity logs & Quick summary
    recent_departments = Department.objects.filter(is_active=True).order_by('-created_at')[:4]
    recent_courses = Course.objects.filter(is_active=True).select_related('department').order_by('-created_at')[:4]

    context = {
        'db_name': settings.DATABASES['default']['NAME'],
        'students_count': students_count,
        'teachers_count': teachers_count,
        'dept_count': dept_count,
        'course_count': course_count,
        'current_year': current_year,
        'current_sem': current_sem,
        'total_fee_billed': total_fee_billed,
        'total_fee_collected': total_fee_collected,
        'total_fee_pending': total_fee_pending,
        'overdue_count': overdue_count,
        'recent_departments': recent_departments,
        'recent_courses': recent_courses,
    }
    return render(request, 'home.html', context)


# ==========================================
# DEPARTMENT MANAGEMENT VIEWS
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
            messages.error(request, "Error creating department. Please check form errors.")
    else:
        form = DepartmentForm()

    return render(request, 'core/departments/department_form.html', {
        'form': form,
        'title': 'Add New Department'
    })


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
            messages.error(request, "Error updating department.")
    else:
        form = DepartmentForm(instance=dept)

    return render(request, 'core/departments/department_form.html', {
        'form': form,
        'title': f"Edit Department - {dept.code}",
        'department': dept
    })


# ==========================================
# COURSE MANAGEMENT VIEWS
# ==========================================

@login_required
def course_list_view(request):
    courses = Course.objects.all().select_related('department')
    search_query = request.GET.get('search', '')
    dept_id = request.GET.get('department', '')

    if search_query:
        courses = courses.filter(name__icontains=search_query) | courses.filter(code__icontains=search_query)
    if dept_id:
        courses = courses.filter(department_id=dept_id)

    departments = Department.objects.filter(is_active=True)

    return render(request, 'core/courses/course_list.html', {
        'courses': courses,
        'departments': departments,
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
            messages.error(request, "Error creating course.")
    else:
        form = CourseForm()

    return render(request, 'core/courses/course_form.html', {
        'form': form,
        'title': 'Add New Course'
    })


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

    return render(request, 'core/courses/course_form.html', {
        'form': form,
        'title': f"Edit Course - {course.code}",
        'course': course
    })


# ==========================================
# ACADEMIC YEAR & SEMESTER MANAGEMENT VIEWS
# ==========================================

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

    return render(request, 'core/academic/academic_years.html', {
        'years': years,
        'form': form
    })


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

    return render(request, 'core/academic/semesters.html', {
        'semesters': semesters,
        'form': form
    })


# ==========================================
# FEE MANAGEMENT VIEWS
# ==========================================

@login_required
def fee_list_view(request):
    fees = StudentFee.objects.all().select_related('student', 'course', 'academic_year')
    
    # Filter for student role vs admin role
    if request.user.is_student:
        fees = fees.filter(student=request.user)

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        fees = fees.filter(
            Q(student__username__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
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

    return render(request, 'core/fees/fee_list.html', {
        'fees': fees,
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
            messages.success(request, f"Fee invoice '{fee.title}' assigned to {fee.student.username} successfully!")
            return redirect('core:fee_list')
        else:
            messages.error(request, "Error creating fee invoice.")
    else:
        form = StudentFeeForm()

    return render(request, 'core/fees/fee_form.html', {
        'form': form,
        'title': 'Create Student Fee Invoice'
    })


@admin_required
def fee_pay_view(request, pk):
    fee = get_object_or_404(StudentFee, pk=pk)
    if request.method == 'POST':
        form = RecordPaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['payment_amount']
            fee.paid_amount += amount
            fee.payment_date = datetime.now()
            fee.save()
            messages.success(request, f"Payment of ₹{amount} recorded for {fee.student.username}. New status: {fee.get_status_display()}.")
            return redirect('core:fee_list')
    else:
        form = RecordPaymentForm(initial={'payment_amount': fee.remaining_due})

    return render(request, 'core/fees/record_payment.html', {
        'fee': fee,
        'form': form
    })
