from django import forms
from django.contrib.auth import get_user_model
from .models import Department, Course, AcademicYear, Semester, StudentProfile, TeacherProfile, Subject, Attendance, ExamMark, StudentFee

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

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'admission_number', 'full_name', 'email', 'phone', 'address', 'gender', 'dob', 'department', 'course', 'academic_year', 'status']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Roll No / Student ID (e.g. 22691A2843)'}),
            'admission_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Admission No'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Institutional Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Full Residential Address'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'dob': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'course': forms.Select(attrs={'class': 'form-input'}),
            'academic_year': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['teacher_id', 'full_name', 'email', 'phone', 'department', 'designation', 'joining_date', 'status']
        widgets = {
            'teacher_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Teacher ID (e.g. T101)'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Faculty Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'designation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Senior Professor'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'course', 'semester', 'credits', 'subject_type', 'assigned_teacher']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Subject Code'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Subject Name'}),
            'course': forms.Select(attrs={'class': 'form-input'}),
            'semester': forms.Select(attrs={'class': 'form-input'}),
            'credits': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'subject_type': forms.Select(attrs={'class': 'form-input'}),
            'assigned_teacher': forms.Select(attrs={'class': 'form-input'}),
        }

class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'attendance_date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-input'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'attendance_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

class ExamMarkForm(forms.ModelForm):
    class Meta:
        model = ExamMark
        fields = ['student', 'exam_name', 'subject', 'marks_obtained', 'total_marks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-input'}),
            'exam_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Mid-term Exam'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Mathematics'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Marks'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '100'}),
        }

class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ['student', 'title', 'fee_type', 'course', 'academic_year', 'total_amount', 'paid_amount', 'payment_method', 'due_date']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Semester 1 Tuition Fee'}),
            'fee_type': forms.Select(attrs={'class': 'form-input'}),
            'course': forms.Select(attrs={'class': 'form-input'}),
            'academic_year': forms.Select(attrs={'class': 'form-input'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'e.g. 45000.00'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'payment_method': forms.Select(choices=[('Cash', 'Cash'), ('Online / UPI', 'Online / UPI'), ('Bank Transfer', 'Bank Transfer'), ('Cheque', 'Cheque')], attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class RecordPaymentForm(forms.Form):
    payment_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Enter payment amount'})
    )
    payment_method = forms.ChoiceField(
        choices=[('Cash', 'Cash'), ('Online / UPI', 'Online / UPI'), ('Bank Transfer', 'Bank Transfer'), ('Cheque', 'Cheque')],
        widget=forms.Select(attrs={'class': 'form-input'})
    )
