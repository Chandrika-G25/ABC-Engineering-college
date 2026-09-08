from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from accounts.decorators import admin_required
from .models import Department, Course, AcademicYear, Semester
from .forms import DepartmentForm, CourseForm, AcademicYearForm, SemesterForm

def home_view(request):
    """
    Renders the central system overview page with stats from core models.
    """
    context = {
        'db_name': settings.DATABASES['default']['NAME'],
        'current_year': 2026,
        'department_count': Department.objects.filter(is_active=True).count(),
        'course_count': Course.objects.filter(is_active=True).count(),
        'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
        'current_semester': Semester.objects.filter(is_current=True).first(),
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
