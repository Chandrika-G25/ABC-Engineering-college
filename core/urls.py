from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    
    # Department URLs
    path('departments/', views.department_list_view, name='department_list'),
    path('departments/add/', views.department_create_view, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_edit_view, name='department_edit'),

    # Course URLs
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/add/', views.course_create_view, name='course_add'),
    path('courses/<int:pk>/edit/', views.course_edit_view, name='course_edit'),

    # Academic Year & Semester URLs
    path('academic-years/', views.academic_year_list_view, name='academic_year_list'),
    path('semesters/', views.semester_list_view, name='semester_list'),

    # Fee Management URLs
    path('fees/', views.fee_list_view, name='fee_list'),
    path('fees/add/', views.fee_create_view, name='fee_add'),
    path('fees/<int:pk>/pay/', views.fee_pay_view, name='fee_pay'),
]
