from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    
    # Students
    path('students/', views.student_list_view, name='student_list'),
    path('students/add/', views.student_create_view, name='student_add'),
    path('students/<int:pk>/edit/', views.student_edit_view, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete_view, name='student_delete'),

    # Teachers & Teacher Attendance
    path('teachers/', views.teacher_list_view, name='teacher_list'),
    path('teachers/add/', views.teacher_create_view, name='teacher_add'),
    path('teachers/<int:pk>/edit/', views.teacher_edit_view, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete_view, name='teacher_delete'),
    path('teacher-attendance/', views.teacher_attendance_list_view, name='teacher_attendance_list'),

    # Student Attendance
    path('attendance/', views.attendance_list_view, name='attendance_list'),

    # Subjects & Marks
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('marks/', views.marks_list_view, name='marks_list'),

    # Fees
    path('fees/', views.fee_list_view, name='fee_list'),
    path('fees/add/', views.fee_create_view, name='fee_add'),
    path('fees/<int:pk>/pay/', views.fee_pay_view, name='fee_pay'),

    # Departments & Courses
    path('departments/', views.department_list_view, name='department_list'),
    path('departments/add/', views.department_create_view, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_edit_view, name='department_edit'),

    path('courses/', views.course_list_view, name='course_list'),
    path('courses/add/', views.course_create_view, name='course_add'),
    path('courses/<int:pk>/edit/', views.course_edit_view, name='course_edit'),

    path('academic-years/', views.academic_year_list_view, name='academic_year_list'),
    path('semesters/', views.semester_list_view, name='semester_list'),

    # Reports
    path('reports/', views.reports_view, name='reports'),
]
