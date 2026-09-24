from django import forms
from django.contrib.auth import get_user_model
from datetime import date
from .models import Department, Course, AcademicYear, Semester, StudentProfile, TeacherProfile, Subject, Attendance, TeacherAttendance, ExamMark, StudentFee

User = get_user_model()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['code', 'name', 'head_of_department', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSE, IT, ECE, EEE, CIVIL, AIDS'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Computer Science & Engineering'}),
            'head_of_department': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Branch Overview'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'department', 'duration_years', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. BTECH-CSE'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. B.Tech Computer Science & Engineering'}),
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
        fields = ['student_id', 'full_name', 'department', 'year', 'email', 'phone', 'status']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Roll No / Student ID (e.g. 22691A0401)'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Student Full Name'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'year': forms.Select(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id', '').strip()
        qs = StudentProfile.objects.filter(student_id__iexact=student_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Roll Number / Student ID '{student_id}' already exists! Duplicate roll numbers are not allowed.")
        return student_id

class TeacherProfileForm(forms.ModelForm):
    joining_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        initial=date.today
    )

    class Meta:
        model = TeacherProfile
        fields = ['teacher_id', 'full_name', 'email', 'phone', 'department', 'designation', 'joining_date', 'status']
        widgets = {
            'teacher_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Teacher ID (e.g. T101)'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Faculty Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Faculty Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'designation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Senior Professor'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_joining_date(self):
        joining_date = self.cleaned_data.get('joining_date')
        if not joining_date:
            return date.today()
        return joining_date

    def clean_teacher_id(self):
        teacher_id = self.cleaned_data.get('teacher_id', '').strip()
        qs = TeacherProfile.objects.filter(teacher_id__iexact=teacher_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Teacher ID '{teacher_id}' already exists!")
        return teacher_id

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
    STREAM_CHOICES = [
        ('', '-- Choose Stream Shortcut --'),
        ('ECE', 'ECE'),
        ('CSE', 'CSE'),
        ('IT', 'IT'),
        ('EEE', 'EEE'),
        ('CIVIL', 'CIVIL'),
        ('AIDS', 'AIDS'),
    ]
    stream = forms.ChoiceField(
        choices=STREAM_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_stream_select'})
    )

    class Meta:
        model = Attendance
        fields = ['stream', 'student', 'subject', 'attendance_date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-input', 'id': 'id_student_select'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'attendance_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }


class TeacherAttendanceForm(forms.ModelForm):
    class Meta:
        model = TeacherAttendance
        fields = ['teacher', 'attendance_date', 'status']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-input'}),
            'attendance_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

class ExamMarkForm(forms.ModelForm):
    class Meta:
        model = ExamMark
        fields = ['student', 'semester', 'exam_name', 'subject_code', 'subject', 'marks_obtained', 'total_marks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-input'}),
            'semester': forms.Select(attrs={'class': 'form-input'}),
            'exam_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. End Semester Exam'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. EC101'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Linear Algebra & Calculus'}),
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
