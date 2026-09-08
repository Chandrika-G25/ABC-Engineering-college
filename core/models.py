from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date

class Department(models.Model):
    """
    Represents an Academic Department (e.g. Computer Science, Mechanical).
    """
    code = models.CharField(max_length=20, unique=True, help_text="Unique Department Code (e.g., CSE, ECE)")
    name = models.CharField(max_length=100, help_text="Full Department Name")
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role': 'TEACHER'},
        help_text="Assigned Head of Department (Teacher)"
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    """
    Represents an Academic Degree Program / Course (e.g. B.Tech CSE, BCA, MCA).
    """
    code = models.CharField(max_length=20, unique=True, help_text="Unique Course Code (e.g., BTECH-CSE)")
    name = models.CharField(max_length=100, help_text="Full Course Degree Name")
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
        help_text="Offering Academic Department"
    )
    duration_years = models.PositiveIntegerField(default=4)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class AcademicYear(models.Model):
    """
    Represents an Academic Year (e.g. 2026-2027).
    """
    name = models.CharField(max_length=20, unique=True, help_text="Academic Year Label (e.g. 2026-2027)")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academic_years'
        ordering = ['-name']

    def __str__(self):
        return f"{self.name} {'(Current)' if self.is_current else ''}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'End date must be strictly after start date.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Semester(models.Model):
    """
    Represents a Semester within an Academic Year (e.g. Semester 1, Semester 2).
    """
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='semesters'
    )
    semester_number = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semesters'
        unique_together = ('academic_year', 'semester_number')
        ordering = ['academic_year', 'semester_number']

    def __str__(self):
        return f"{self.academic_year.name} - {self.name}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'Semester end date must be strictly after start date.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_current:
            Semester.objects.filter(academic_year=self.academic_year, is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class TeacherProfile(models.Model):
    """
    Represents a Faculty Teacher profile.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        null=True, blank=True
    )
    teacher_id = models.CharField(max_length=50, unique=True, help_text="Unique Teacher ID")
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=100, default='Assistant Professor')
    joining_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher_profiles'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.teacher_id})"


class StudentProfile(models.Model):
    """
    Represents a Student profile containing personal, contact, and academic details.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        null=True, blank=True
    )
    student_id = models.CharField(max_length=50, unique=True, help_text="Roll No / Student ID (e.g. 22691A2843)")
    admission_number = models.CharField(max_length=50, unique=True, help_text="Admission Serial Number")
    full_name = models.CharField(max_length=150)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    admission_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Graduated', 'Graduated'), ('Suspended', 'Suspended')], default='Active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        ordering = ['student_id']

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


class Subject(models.Model):
    """
    Represents an Academic Subject (Theory, Practical, Elective).
    """
    code = models.CharField(max_length=20, unique=True, help_text="Subject Code (e.g. CS101)")
    name = models.CharField(max_length=100, help_text="Subject Name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    credits = models.PositiveIntegerField(default=3)
    subject_type = models.CharField(max_length=20, choices=[('Theory', 'Theory'), ('Practical', 'Practical'), ('Elective', 'Elective')], default='Theory')
    assigned_teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Attendance(models.Model):
    """
    Represents Daily Student Attendance Records.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    attendance_date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')], default='Present')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance'
        ordering = ['-attendance_date']

    def __str__(self):
        return f"{self.student.student_id} - {self.attendance_date} ({self.status})"


class ExamMark(models.Model):
    """
    Represents Examination Marks Records.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='exam_marks')
    exam_name = models.CharField(max_length=100, help_text="e.g. Mid-term, Final Exam")
    subject = models.CharField(max_length=100, help_text="Subject Name")
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exam_marks'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.student_id} - {self.exam_name} ({self.marks_obtained}/{self.total_marks})"

    @property
    def percentage(self):
        if self.total_marks > 0:
            return round((self.marks_obtained / self.total_marks) * 100, 2)
        return 0.00

    @property
    def grade(self):
        p = self.percentage
        if p >= 90: return 'A+'
        if p >= 80: return 'A'
        if p >= 70: return 'B'
        if p >= 60: return 'C'
        if p >= 50: return 'D'
        return 'F'


class StudentFee(models.Model):
    """
    Represents Student Fee Invoices & Payment Tracking.
    """
    FEE_TYPE_TUITION = 'TUITION'
    FEE_TYPE_ADMISSION = 'ADMISSION'
    FEE_TYPE_EXAM = 'EXAM'
    FEE_TYPE_HOSTEL = 'HOSTEL'
    FEE_TYPE_OTHER = 'OTHER'

    FEE_TYPE_CHOICES = [
        (FEE_TYPE_TUITION, 'Tuition Fee'),
        (FEE_TYPE_ADMISSION, 'Admission Fee'),
        (FEE_TYPE_EXAM, 'Examination Fee'),
        (FEE_TYPE_HOSTEL, 'Hostel Fee'),
        (FEE_TYPE_OTHER, 'Other / Miscellaneous'),
    ]

    STATUS_PAID = 'PAID'
    STATUS_PARTIAL = 'PARTIAL'
    STATUS_PENDING = 'PENDING'
    STATUS_OVERDUE = 'OVERDUE'

    STATUS_CHOICES = [
        (STATUS_PAID, 'Paid'),
        (STATUS_PARTIAL, 'Partially Paid'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_OVERDUE, 'Overdue'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='fee_invoices',
        null=True, blank=True
    )
    user_account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    title = models.CharField(max_length=100, help_text="Invoice Title (e.g. Semester 1 Tuition Fee)")
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default=FEE_TYPE_TUITION)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default='Online / UPI')
    due_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_fees'
        ordering = ['-due_date']

    def __str__(self):
        s_name = self.student.full_name if self.student else "Student"
        return f"{s_name} - {self.title} (₹{self.paid_amount}/₹{self.total_amount})"

    @property
    def remaining_due(self):
        return self.total_amount - self.paid_amount

    def update_status(self):
        if self.paid_amount >= self.total_amount:
            self.status = self.STATUS_PAID
        elif self.paid_amount > 0:
            self.status = self.STATUS_PARTIAL
        elif self.due_date < date.today():
            self.status = self.STATUS_OVERDUE
        else:
            self.status = self.STATUS_PENDING

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)
