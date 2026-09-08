from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

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
    A Department can offer multiple Courses.
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
    Enforces business rule: Only one academic year can be set as current active at any time.
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
            # Enforce single active academic year business rule
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
    semester_number = models.PositiveIntegerField(help_text="Semester Number (e.g. 1, 2, 3, 4, 5, 6, 7, 8)")
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
            # Enforce single active current semester per academic year
            Semester.objects.filter(academic_year=self.academic_year, is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)
