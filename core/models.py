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
    is_active = models.BooleanField(default=True, help_text="Active status of the department")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    """
    Represents an Academic Degree Program / Course (e.g. B.Tech Computer Science, BCA, MCA).
    """
    code = models.CharField(max_length=20, unique=True, help_text="Unique Course Code (e.g., BTECH-CSE)")
    name = models.CharField(max_length=100, help_text="Full Course Degree Name")
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
        help_text="Offering Academic Department"
    )
    duration_years = models.PositiveIntegerField(default=4, help_text="Duration in years")
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
    is_current = models.BooleanField(default=False, help_text="Currently active academic year")
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
        related_name='semesters',
        help_text="Associated Academic Year"
    )
    semester_number = models.PositiveIntegerField(help_text="Semester Number (e.g. 1, 2, 3, 4)")
    name = models.CharField(max_length=50, help_text="Semester Display Name (e.g. Semester 1)")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, help_text="Currently active semester")
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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fee_invoices',
        help_text="Student account"
    )
    title = models.CharField(max_length=100, help_text="Invoice Title (e.g. Semester 1 Tuition Fee)")
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default=FEE_TYPE_TUITION)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total fee amount")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount paid so far")
    due_date = models.DateField(help_text="Payment due date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_fees'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.student.username} - {self.title} (₹{self.paid_amount}/₹{self.total_amount})"

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
