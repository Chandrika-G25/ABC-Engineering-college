from django import forms
from django.contrib.auth import get_user_model
from .models import Department, Course, AcademicYear, Semester, StudentFee

User = get_user_model()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['code', 'name', 'head_of_department', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSE'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Department of Computer Science'}),
            'head_of_department': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Department Description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'department', 'duration_years', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. BTECH-CSE'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Bachelor of Technology in CSE'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 6}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Course Overview'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 2026-2027'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['academic_year', 'semester_number', 'name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'academic_year': forms.Select(attrs={'class': 'form-input'}),
            'semester_number': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 12}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Semester 1'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class StudentFeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(role=User.ROLE_STUDENT)

    class Meta:
        model = StudentFee
        fields = ['student', 'title', 'fee_type', 'course', 'academic_year', 'total_amount', 'paid_amount', 'due_date']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Semester 1 Tuition Fee'}),
            'fee_type': forms.Select(attrs={'class': 'form-input'}),
            'course': forms.Select(attrs={'class': 'form-input'}),
            'academic_year': forms.Select(attrs={'class': 'form-input'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'e.g. 45000.00'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class RecordPaymentForm(forms.Form):
    payment_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Enter payment amount'})
    )
