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

    # Teachers
    path('teachers/', views.teacher_list_view, name='teacher_list'),

    # Subjects
    path('subjects/', views.subject_list_view, name='subject_list'),

    # Attendance
    path('attendance/', views.attendance_list_view, name='attendance_list'),

    # Examination Marks
    path('marks/', views.marks_list_view, name='marks_list'),

    # Fee Management
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
