import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum, Q, Count
from django.contrib.auth import get_user_model
from datetime import datetime, date
from django.utils import timezone
from accounts.decorators import admin_required, teacher_required
from .models import Department, Course, AcademicYear, Semester, StudentProfile, TeacherProfile, Subject, Attendance, TeacherAttendance, ExamMark, StudentFee
from .forms import (
    DepartmentForm, CourseForm, AcademicYearForm, SemesterForm,
    StudentProfileForm, TeacherProfileForm, SubjectForm, AttendanceRecordForm,
    TeacherAttendanceForm, ExamMarkForm, StudentFeeForm, RecordPaymentForm
)
from .curriculum import (
    get_student_results_matrix, STREAM_METADATA, YEAR_CHOICES, ALL_8_SEMESTERS,
    get_allowed_semesters_for_year, get_primary_semesters_for_year, CURRICULUM_DATA,
    get_fee_collection_matrix
)

User = get_user_model()

@login_required
def home_view(request):
    """
    B.Tech College Management Control Dashboard with stream-wise details & structured dashboards.
    """
    students_count = StudentProfile.objects.filter(status='Active').count()
    teachers_count = TeacherProfile.objects.filter(status='Active').count()
    student_attendance_count = Attendance.objects.count()
    teacher_attendance_count = TeacherAttendance.objects.count()
    dept_count = Department.objects.filter(is_active=True).count()
    course_count = Course.objects.filter(is_active=True).count()

    current_year = AcademicYear.objects.filter(is_current=True).first()
    current_sem = Semester.objects.filter(is_current=True).first()

    # Fee metrics calculation
    fee_aggregates = StudentFee.objects.aggregate(
        total=Sum('total_amount'),
        paid=Sum('paid_amount')
    )
    total_fee_billed = fee_aggregates['total'] or 0.00
    total_fee_collected = fee_aggregates['paid'] or 0.00
    total_fee_pending = total_fee_billed - total_fee_collected

    recent_students = StudentProfile.objects.all().select_related('course', 'department').order_by('-created_at')[:12]
    recent_teachers = TeacherProfile.objects.all().select_related('department').order_by('-created_at')[:10]

    # Stream breakdown metrics with custom color themes & icons for Students and Faculty
    stream_data = [
        {
            'code': 'ECE',
            'name': 'Electronics & Comm.',
            'roll_prefix': '22691A04xx',
            'count': StudentProfile.objects.filter(department__code='ECE').count(),
            'teacher_count': TeacherProfile.objects.filter(department__code='ECE').count(),
            'bg_gradient': 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
            'border_color': '#fde68a',
            'text_color': '#92400e',
            'badge_bg': '#ffffff',
            'badge_text': '#b45309',
            'icon': 'fa-microchip',
            'accent': '#d97706'
        },
        {
            'code': 'CSE',
            'name': 'Computer Science & Eng.',
            'roll_prefix': '22691A05xx',
            'count': StudentProfile.objects.filter(department__code='CSE').count(),
            'teacher_count': TeacherProfile.objects.filter(department__code='CSE').count(),
            'bg_gradient': 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
            'border_color': '#bfdbfe',
            'text_color': '#1e40af',
            'badge_bg': '#ffffff',
            'badge_text': '#1d4ed8',
            'icon': 'fa-laptop-code',
            'accent': '#2563eb'
        },
        {
            'code': 'IT',
            'name': 'Information Tech.',
            'roll_prefix': '22691A12xx',
            'count': StudentProfile.objects.filter(department__code='IT').count(),
            'teacher_count': TeacherProfile.objects.filter(department__code='IT').count(),
            'bg_gradient': 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
            'border_color': '#a7f3d0',
            'text_color': '#065f46',
            'badge_bg': '#ffffff',
            'badge_text': '#047857',
            'icon': 'fa-network-wired',
            'accent': '#059669'
        },
        {
            'code': 'EEE',
            'name': 'Electrical & Electronics',
            'roll_prefix': '22691A02xx',
            'count': StudentProfile.objects.filter(department__code='EEE').count(),
            'teacher_count': TeacherProfile.objects.filter(department__code='EEE').count(),
            'bg_gradient': 'linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%)',
            'border_color': '#f5d0fe',
            'text_color': '#86198f',
            'badge_bg': '#ffffff',
            'badge_text': '#a21caf',
            'icon': 'fa-bolt',
            'accent': '#c026d3'
        },
        {
            'code': 'CIVIL',
            'name': 'Civil Engineering',
            'roll_prefix': '22691A01xx',
            'count': StudentProfile.objects.filter(department__code='CIVIL').count(),
            'teacher_count': TeacherProfile.objects.filter(department__code='CIVIL').count(),
            'bg_gradient': 'linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%)',
            'border_color': '#fecdd3',
            'text_color': '#9f1239',
            'badge_bg': '#ffffff',
            'badge_text': '#be123c',
            'icon': 'fa-building',
            'accent': '#e11d48'
        },
        {
            'code': 'AIDS',
            'name': 'AI & Data Science',
            'roll_prefix': '22691A32xx',
            'count': StudentProfile.objects.filter(department__code='AIDS').count(),
            'teacher_count': TeacherProfile.objects.filter(department__code='AIDS').count(),
            'bg_gradient': 'linear-gradient(135deg, #ecfeff 0%, #cffaff 100%)',
            'border_color': '#a5f3fc',
            'text_color': '#155e75',
            'badge_bg': '#ffffff',
            'badge_text': '#0e7490',
            'icon': 'fa-brain',
            'accent': '#0891b2'
        },
    ]

    # Calculate year-wise student counts for each department (for Student Stream & Year Directory)
    years_list = ['I', 'II', 'III', 'IV']
    year_counts_raw = StudentProfile.objects.values('department__code', 'year').annotate(c=Count('id'))
    dept_year_counts = {}
    for item in year_counts_raw:
        d_code = item['department__code']
        yr = item['year']
        if d_code:
            dept_year_counts.setdefault(d_code, {})[yr] = item['c']

    for s in stream_data:
        s['year_breakdown'] = [
            {
                'year': y,
                'count': dept_year_counts.get(s['code'], {}).get(y, 0)
            }
            for y in years_list
        ]

    # Section 3: Marks & Results Matrix Context
    marks_stream = request.GET.get('marks_stream', 'ECE').strip()
    marks_year = request.GET.get('marks_year', 'I').strip()
    marks_sem = request.GET.get('marks_sem', '').strip()
    marks_search = request.GET.get('marks_search', '').strip()

    # Handle Record Examination Marks from Dashboard Modal
    if request.method == 'POST' and request.POST.get('record_marks'):
        student_id = request.POST.get('student') or request.POST.get('student_roll_select') or request.POST.get('student_name_select')
        semester = request.POST.get('semester')
        subject_code = request.POST.get('subject_code', '').strip()
        subject_name = request.POST.get('subject', '').strip()
        marks_obtained = request.POST.get('marks_obtained')
        total_marks = request.POST.get('total_marks', '100.00')

        if student_id and semester and (subject_code or subject_name) and marks_obtained:
            student = get_object_or_404(StudentProfile, id=student_id)
            try:
                dec_obtained = Decimal(marks_obtained)
                dec_total = Decimal(total_marks or '100.00')
            except Exception:
                messages.error(request, "Invalid marks values entered. Please enter a valid number.")
                return redirect(f"{reverse('core:home')}#marks-results")

            allowed_sems = get_allowed_semesters_for_year(student.year)
            if semester not in allowed_sems:
                messages.error(request, f"Semester {semester} is not valid for {student.year} Year students. Allowed: {', '.join(allowed_sems)}.")
            else:
                ExamMark.objects.update_or_create(
                    student=student,
                    semester=semester,
                    subject_code=subject_code or subject_name[:6].upper(),
                    defaults={
                        'subject': subject_name or subject_code,
                        'exam_name': f"{semester} Final Examination",
                        'marks_obtained': dec_obtained,
                        'total_marks': dec_total,
                    }
                )
                messages.success(request, f"Marks ({marks_obtained}/{total_marks}) successfully recorded for {student.full_name} ({student.student_id}) in {subject_name or subject_code} - {semester}!")
                stream_code = student.department.code if student.department else 'ECE'
                return redirect(f"{reverse('core:home')}?marks_stream={stream_code}&marks_year={student.year}&marks_sem={semester}#marks-results")

    # Handle Record Fee Payment from Dashboard Modal
    if request.method == 'POST' and request.POST.get('record_fee_payment'):
        student_id = request.POST.get('student') or request.POST.get('student_roll_select') or request.POST.get('student_name_select')
        semester = request.POST.get('semester')
        payment_amount = request.POST.get('payment_amount')
        payment_method = request.POST.get('payment_method', 'Online / UPI')

        if student_id and semester and payment_amount:
            student = get_object_or_404(StudentProfile, id=student_id)
            try:
                dec_payment = Decimal(payment_amount)
                if dec_payment <= 0:
                    raise ValueError("Amount must be positive")
            except Exception:
                messages.error(request, "Invalid payment amount entered. Please enter a valid positive number.")
                return redirect(f"{reverse('core:home')}#fee-collection")

            allowed_sems = get_allowed_semesters_for_year(student.year)
            if semester not in allowed_sems:
                messages.error(request, f"Semester {semester} is not eligible for {student.year} Year students to pay. Allowed: {', '.join(allowed_sems)}.")
            else:
                fee, _ = StudentFee.objects.get_or_create(
                    student=student,
                    semester=semester,
                    defaults={
                        'title': f'{semester} B.Tech Tuition Fee',
                        'fee_type': StudentFee.FEE_TYPE_TUITION,
                        'total_amount': Decimal('70000.00'),
                        'paid_amount': Decimal('0.00'),
                    }
                )
                fee.total_amount = Decimal('70000.00')
                fee.paid_amount += dec_payment
                fee.payment_method = payment_method
                fee.payment_date = timezone.now()
                fee.save()
                messages.success(request, f"Fee payment of ₹{dec_payment:,.2f} recorded for {student.full_name} ({student.student_id}) in {semester}! Remaining Balance Due: ₹{fee.remaining_due:,.2f}.")
                stream_code = student.department.code if student.department else 'ECE'
                return redirect(f"{reverse('core:home')}?fee_stream={stream_code}&fee_year={student.year}&fee_sem={semester}#fee-collection")
        else:
            messages.error(request, "Error recording fee payment. Please fill in all required fields.")
            return redirect(f"{reverse('core:home')}#fee-collection")

    marks_results = get_student_results_matrix(
        stream_code=marks_stream,
        year=marks_year,
        semester=marks_sem,
        search_query=marks_search
    )

    fee_stream = request.GET.get('fee_stream', 'ECE').strip()
    fee_year = request.GET.get('fee_year', 'I').strip()
    fee_sem = request.GET.get('fee_sem', '').strip()
    fee_search = request.GET.get('fee_search', '').strip()
    fee_status = request.GET.get('fee_status', '').strip()

    fee_results = get_fee_collection_matrix(
        stream_code=fee_stream,
        year=fee_year,
        semester=fee_sem or None,
        search_query=fee_search,
        status_filter=fee_status
    )

    all_fees_lookup = {
        f"{f.student_id}_{f.semester}": {
            'total': float(f.total_amount),
            'paid': float(f.paid_amount),
            'due': float(f.remaining_due)
        }
        for f in StudentFee.objects.all().select_related('student')
    }

    active_students = StudentProfile.objects.filter(status='Active').select_related('department').order_by('student_id')
    students_for_modal = [
        {
            'id': sp.id,
            'roll_no': sp.student_id,
            'full_name': sp.full_name,
            'stream': sp.department.code if sp.department else 'ECE',
            'year': sp.year or 'I',
        }
        for sp in active_students
    ]

    context = {
        'db_name': settings.DATABASES['default']['NAME'],
        'students_count': students_count,
        'teachers_count': teachers_count,
        'student_attendance_count': student_attendance_count,
        'teacher_attendance_count': teacher_attendance_count,
        'dept_count': dept_count,
        'course_count': course_count,
        'current_year': current_year,
        'current_sem': current_sem,
        'total_fee_billed': total_fee_billed,
        'total_fee_collected': total_fee_collected,
        'total_fee_pending': total_fee_pending,
        'recent_students': recent_students,
        'recent_teachers': recent_teachers,
        'stream_data': stream_data,
        'marks_results': marks_results,
        'fee_results': fee_results,
        'active_students': active_students,
        'students_json': json.dumps(students_for_modal),
        'curriculum_json': json.dumps(CURRICULUM_DATA),
        'fee_students_json': json.dumps(students_for_modal),
        'fee_lookup_json': json.dumps(all_fees_lookup),
    }
    return render(request, 'home.html', context)


# ==========================================
# CONSOLIDATED STUDENT MANAGEMENT VIEW
# ==========================================

@login_required
def student_list_view(request):
    students = StudentProfile.objects.all().select_related('course', 'department')
    search_query = request.GET.get('search', '').strip()
    dept_code = request.GET.get('dept', '').strip()
    course_id = request.GET.get('course', '').strip()
    selected_year = request.GET.get('year', '').strip()

    if search_query and not dept_code:
        dept_match = Department.objects.filter(code__iexact=search_query).first()
        if dept_match:
            dept_code = dept_match.code
            search_query = ''

    if not dept_code and not search_query and not selected_year:
        dept_code = 'ECE'

    if not selected_year and not search_query and not request.GET.get('dept'):
        selected_year = 'I'

    if dept_code and dept_code.upper() != 'ALL':
        students = students.filter(department__code__iexact=dept_code)
    elif search_query:
        students = students.filter(
            Q(full_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__code__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    if selected_year and selected_year.upper() != 'ALL':
        students = students.filter(year__iexact=selected_year)

    if course_id:
        students = students.filter(course_id=course_id)

    if request.method == 'POST' and request.user.is_admin_user:
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            st = form.save(commit=False)
            if st.department and not st.course:
                st.course = Course.objects.filter(department=st.department).first()
            st.save()
            messages.success(request, f"Student '{st.full_name}' ({st.student_id}) registered successfully under {st.department.code if st.department else 'ECE'} Stream!")
            target_dept = st.department.code if st.department else 'ECE'
            target_year = st.year or 'I'
            return redirect(f"{reverse('core:student_list')}?dept={target_dept}&year={target_year}")
        else:
            messages.error(request, "Error adding student. Please check form errors.")
    else:
        form = StudentProfileForm()

    return render(request, 'core/students/student_list.html', {
        'students': students,
        'form': form,
        'search_query': search_query,
        'selected_dept': dept_code,
        'selected_year': selected_year,
        'selected_course': course_id,
        'courses': Course.objects.filter(is_active=True)
    })


@admin_required
def student_create_view(request):
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            st = form.save(commit=False)
            if st.department and not st.course:
                st.course = Course.objects.filter(department=st.department).first()
            st.save()
            messages.success(request, f"Student '{st.full_name}' ({st.student_id}) registered successfully under {st.department.code if st.department else 'ECE'} Stream!")
            target_dept = st.department.code if st.department else 'ECE'
            target_year = st.year or 'I'
            return redirect(f"{reverse('core:student_list')}?dept={target_dept}&year={target_year}")
        else:
            messages.error(request, "Error adding student. Please check form errors.")
    else:
        form = StudentProfileForm()
    return render(request, 'core/students/student_form.html', {'form': form, 'title': 'Register New Student'})


@admin_required
def student_edit_view(request, pk):
    st = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=st)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{st.full_name}' updated successfully.")
            return redirect('core:student_list')
    else:
        form = StudentProfileForm(instance=st)
    return render(request, 'core/students/student_form.html', {'form': form, 'title': f"Edit Student - {st.student_id}", 'student': st})


@admin_required
def student_delete_view(request, pk):
    st = get_object_or_404(StudentProfile, pk=pk)
    st_name = st.full_name
    st.delete()
    messages.success(request, f"Student '{st_name}' deleted successfully.")
    return redirect('core:student_list')


# ==========================================
# CONSOLIDATED TEACHER MANAGEMENT VIEW
# ==========================================

@login_required
def teacher_list_view(request):
    teachers = TeacherProfile.objects.all().select_related('department')
    search_query = request.GET.get('search', '')
    dept_code = request.GET.get('dept', '')

    if dept_code and not search_query:
        search_query = dept_code

    if search_query:
        teachers = teachers.filter(
            Q(full_name__icontains=search_query) |
            Q(teacher_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__code__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    if request.method == 'POST' and request.user.is_admin_user:
        form = TeacherProfileForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Faculty Member '{t.full_name}' ({t.teacher_id}) registered successfully!")
            return redirect('core:teacher_list')
        else:
            messages.error(request, "Error registering faculty member. Please check form inputs.")
    else:
        form = TeacherProfileForm()

    return render(request, 'core/teachers/teacher_list.html', {
        'teachers': teachers,
        'form': form,
        'search_query': search_query
    })


@admin_required
def teacher_create_view(request):
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Faculty Member '{t.full_name}' ({t.teacher_id}) registered successfully!")
            return redirect('core:teacher_list')
        else:
            messages.error(request, "Error registering faculty member. Please check form inputs.")
    else:
        form = TeacherProfileForm()
    return render(request, 'core/teachers/teacher_form.html', {'form': form, 'title': 'Register New Faculty Member'})


@admin_required
def teacher_edit_view(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f"Faculty Member '{teacher.full_name}' updated successfully.")
            return redirect('core:teacher_list')
    else:
        form = TeacherProfileForm(instance=teacher)
    return render(request, 'core/teachers/teacher_form.html', {'form': form, 'title': f"Edit Faculty - {teacher.teacher_id}", 'teacher': teacher})


@admin_required
def teacher_delete_view(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    t_name = teacher.full_name
    teacher.delete()
    messages.success(request, f"Faculty Member '{t_name}' deleted successfully.")
    return redirect('core:teacher_list')


# ==========================================
# STUDENT & TEACHER ATTENDANCE VIEWS
# ==========================================

@login_required
def attendance_list_view(request):
    selected_stream = request.GET.get('stream', '') or request.POST.get('stream', '')
    selected_subject_id = request.GET.get('subject', '') or request.POST.get('subject', '')
    selected_year = request.GET.get('year', '') or request.POST.get('year', '')
    records = Attendance.objects.all().select_related('student', 'student__department', 'subject')
    students = StudentProfile.objects.filter(status='Active').select_related('department')
    subjects = Subject.objects.all()

    streams_summary = [
        {'code': 'ECE', 'name': 'Electronics & Communication', 'color': '#d97706', 'bg': '#fef3c7', 'border': '#fde68a', 'icon': 'fa-microchip'},
        {'code': 'CSE', 'name': 'Computer Science & Engineering', 'color': '#2563eb', 'bg': '#eff6ff', 'border': '#bfdbfe', 'icon': 'fa-laptop-code'},
        {'code': 'IT', 'name': 'Information Technology', 'color': '#059669', 'bg': '#ecfdf5', 'border': '#a7f3d0', 'icon': 'fa-network-wired'},
        {'code': 'EEE', 'name': 'Electrical & Electronics', 'color': '#c026d3', 'bg': '#fdf4ff', 'border': '#f5d0fe', 'icon': 'fa-bolt'},
        {'code': 'CIVIL', 'name': 'Civil Engineering', 'color': '#e11d48', 'bg': '#fff1f2', 'border': '#fecdd3', 'icon': 'fa-building'},
        {'code': 'AIDS', 'name': 'AI & Data Science', 'color': '#0891b2', 'bg': '#ecfeff', 'border': '#a5f3fc', 'icon': 'fa-brain'},
    ]

    for item in streams_summary:
        item['student_count'] = StudentProfile.objects.filter(department__code=item['code'], status='Active').count()

    if selected_stream:
        records = records.filter(student__department__code=selected_stream)
        students = students.filter(department__code=selected_stream)
        subjects = subjects.filter(course__department__code=selected_stream)
        if not selected_year:
            selected_year = 'I'

    if selected_year:
        records = records.filter(student__year=selected_year)
        students = students.filter(year=selected_year)

    selected_subject_obj = None
    if selected_stream and subjects.exists():
        if selected_subject_id:
            try:
                selected_subject_obj = subjects.get(pk=selected_subject_id)
            except (ValueError, Subject.DoesNotExist):
                selected_subject_obj = subjects.first()
        else:
            selected_subject_obj = subjects.first()

    if selected_subject_obj:
        records = records.filter(subject=selected_subject_obj)

    if request.method == 'POST':
        form = AttendanceRecordForm(request.POST)
        if selected_stream:
            form.fields['student'].queryset = students
            form.fields['subject'].queryset = subjects
        if form.is_valid():
            att = form.save(commit=False)
            att_obj, created = Attendance.objects.update_or_create(
                student=att.student,
                subject=att.subject,
                attendance_date=att.attendance_date,
                defaults={
                    'status': att.status,
                    'recorded_by': request.user
                }
            )
            dept_code = att_obj.student.department.code if att_obj.student.department else ''
            sub_name = att_obj.subject.name if att_obj.subject else 'General Academic'
            action_str = "marked" if created else "updated to"
            messages.success(request, f"Attendance {action_str} '{att_obj.status}' for {att_obj.student.full_name} in [{sub_name}].")
            redirect_url = f"{reverse('core:attendance_list')}?stream={selected_stream}"
            if att_obj.subject:
                redirect_url += f"&subject={att_obj.subject.pk}"
            if selected_year:
                redirect_url += f"&year={selected_year}"
            return redirect(redirect_url)
        else:
            messages.error(request, f"Error saving attendance record. Please check inputs: {form.errors.as_text()}")
    else:
        initial_dict = {'attendance_date': date.today()}
        if selected_stream:
            initial_dict['stream'] = selected_stream
        if selected_subject_obj:
            initial_dict['subject'] = selected_subject_obj
        form = AttendanceRecordForm(initial=initial_dict)
        if selected_stream:
            form.fields['student'].queryset = students
            form.fields['subject'].queryset = subjects

    return render(request, 'core/attendance/attendance_list.html', {
        'records': records,
        'students': students,
        'subjects': subjects,
        'form': form,
        'selected_stream': selected_stream,
        'selected_subject': selected_subject_obj,
        'selected_year': selected_year,
        'streams_summary': streams_summary
    })


@login_required
def teacher_attendance_list_view(request):
    selected_stream = request.GET.get('stream', 'ECE').strip().upper()
    today_date = date.today()

    streams = ['ECE', 'CSE', 'IT', 'EEE', 'CIVIL', 'AIDS']
    stream_tabs = []
    for s in streams:
        count = TeacherProfile.objects.filter(department__code__iexact=s, status='Active').count()
        stream_tabs.append({'code': s, 'count': count})
    all_count = TeacherProfile.objects.filter(status='Active').count()

    teachers = TeacherProfile.objects.filter(status='Active').select_related('department').order_by('teacher_id')
    records = TeacherAttendance.objects.all().select_related('teacher', 'teacher__department').order_by('-attendance_date', '-created_at')

    if selected_stream != 'ALL':
        teachers = teachers.filter(department__code__iexact=selected_stream)
        records = records.filter(teacher__department__code__iexact=selected_stream)

    # Attach today's attendance status to each teacher
    today_attendance = TeacherAttendance.objects.filter(attendance_date=today_date)
    today_status_map = {att.teacher_id: att.status for att in today_attendance}
    for t in teachers:
        t.today_status = today_status_map.get(t.id, 'Not Marked')

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1-Click quick attendance marking for single teacher
        if action == 'quick_mark':
            teacher_id = request.POST.get('teacher_id')
            status = request.POST.get('status', 'Present')
            t = get_object_or_404(TeacherProfile, id=teacher_id)
            TeacherAttendance.objects.update_or_create(
                teacher=t,
                attendance_date=today_date,
                defaults={'status': status, 'recorded_by': request.user}
            )
            messages.success(request, f"Marked '{status}' for {t.full_name} ({t.department.code if t.department else ''}).")
            return redirect(f"{reverse('core:teacher_attendance_list')}?stream={selected_stream}")

        # Bulk 1-Click mark all stream faculty as Present
        elif action == 'mark_all_stream_present':
            count = 0
            for t in teachers:
                TeacherAttendance.objects.update_or_create(
                    teacher=t,
                    attendance_date=today_date,
                    defaults={'status': 'Present', 'recorded_by': request.user}
                )
                count += 1
            messages.success(request, f"Successfully marked all {count} {selected_stream} faculty members as Present for today ({today_date})!")
            return redirect(f"{reverse('core:teacher_attendance_list')}?stream={selected_stream}")

        # Standard form submission
        else:
            form = TeacherAttendanceForm(request.POST)
            if form.is_valid():
                t_att = form.save(commit=False)
                t_att.recorded_by = request.user
                t_att.save()
                messages.success(request, f"Attendance marked '{t_att.status}' for {t_att.teacher.full_name}.")
                stream_redirect = t_att.teacher.department.code if t_att.teacher.department else selected_stream
                return redirect(f"{reverse('core:teacher_attendance_list')}?stream={stream_redirect}")
    else:
        form = TeacherAttendanceForm(initial={'attendance_date': today_date})
        if selected_stream != 'ALL':
            form.fields['teacher'].queryset = teachers

    return render(request, 'core/attendance/teacher_attendance_list.html', {
        'records': records[:50],
        'teachers': teachers,
        'form': form,
        'selected_stream': selected_stream,
        'stream_tabs': stream_tabs,
        'all_count': all_count,
        'today_date': today_date,
    })


# ==========================================
# MARKS & FEES VIEWS
# ==========================================

@login_required
def marks_list_view(request):
    marks_stream = request.GET.get('marks_stream', 'ECE').strip()
    marks_year = request.GET.get('marks_year', 'I').strip()
    marks_sem = request.GET.get('marks_sem', '').strip()
    marks_search = request.GET.get('marks_search', '').strip()

    if request.method == 'POST':
        student_id = request.POST.get('student') or request.POST.get('student_roll_select') or request.POST.get('student_name_select')
        semester = request.POST.get('semester')
        subject_code = request.POST.get('subject_code', '').strip()
        subject_name = request.POST.get('subject', '').strip()
        marks_obtained = request.POST.get('marks_obtained')
        total_marks = request.POST.get('total_marks', '100.00')

        if student_id and semester and (subject_code or subject_name) and marks_obtained:
            student = get_object_or_404(StudentProfile, id=student_id)
            try:
                dec_obtained = Decimal(marks_obtained)
                dec_total = Decimal(total_marks or '100.00')
            except Exception:
                messages.error(request, "Invalid marks values entered. Please enter a valid number.")
                return redirect(reverse('core:marks_list'))

            allowed_sems = get_allowed_semesters_for_year(student.year)
            if semester not in allowed_sems:
                messages.error(request, f"Semester {semester} is not valid for {student.year} Year students. Allowed: {', '.join(allowed_sems)}.")
            else:
                ExamMark.objects.update_or_create(
                    student=student,
                    semester=semester,
                    subject_code=subject_code or subject_name[:6].upper(),
                    defaults={
                        'subject': subject_name or subject_code,
                        'exam_name': f"{semester} Final Examination",
                        'marks_obtained': dec_obtained,
                        'total_marks': dec_total,
                    }
                )
                messages.success(request, f"Marks ({marks_obtained}/{total_marks}) successfully recorded for {student.full_name} ({student.student_id}) in {subject_name or subject_code} - {semester}!")
                stream_code = student.department.code if student.department else 'ECE'
                return redirect(f"{reverse('core:marks_list')}?marks_stream={stream_code}&marks_year={student.year}&marks_sem={semester}")
        else:
            messages.error(request, "Error recording marks. Please fill in all required fields.")

    form = ExamMarkForm(initial={'semester': marks_sem or 'Sem I'})

    marks_results = get_student_results_matrix(
        stream_code=marks_stream,
        year=marks_year,
        semester=marks_sem,
        search_query=marks_search
    )

    active_students = StudentProfile.objects.filter(status='Active').select_related('department').order_by('student_id')
    students_for_modal = [
        {
            'id': sp.id,
            'roll_no': sp.student_id,
            'full_name': sp.full_name,
            'stream': sp.department.code if sp.department else 'ECE',
            'year': sp.year or 'I',
        }
        for sp in active_students
    ]

    return render(request, 'core/marks/marks_list.html', {
        'marks_results': marks_results,
        'form': form,
        'active_students': active_students,
        'students_json': json.dumps(students_for_modal),
        'curriculum_json': json.dumps(CURRICULUM_DATA),
    })


@login_required
def fee_list_view(request):
    # Handle Record Fee Payment from Modal
    if request.method == 'POST' and request.POST.get('record_fee_payment'):
        student_id = request.POST.get('student') or request.POST.get('student_roll_select') or request.POST.get('student_name_select')
        semester = request.POST.get('semester')
        payment_amount = request.POST.get('payment_amount')
        payment_method = request.POST.get('payment_method', 'Online / UPI')

        if student_id and semester and payment_amount:
            student = get_object_or_404(StudentProfile, id=student_id)
            try:
                dec_payment = Decimal(payment_amount)
                if dec_payment <= 0:
                    raise ValueError("Amount must be positive")
            except Exception:
                messages.error(request, "Invalid payment amount entered. Please enter a valid positive number.")
                return redirect('core:fee_list')

            allowed_sems = get_allowed_semesters_for_year(student.year)
            if semester not in allowed_sems:
                messages.error(request, f"Semester {semester} is not eligible for {student.year} Year students to pay. Allowed: {', '.join(allowed_sems)}.")
            else:
                fee, _ = StudentFee.objects.get_or_create(
                    student=student,
                    semester=semester,
                    defaults={
                        'title': f'{semester} B.Tech Tuition Fee',
                        'fee_type': StudentFee.FEE_TYPE_TUITION,
                        'total_amount': Decimal('70000.00'),
                        'paid_amount': Decimal('0.00'),
                    }
                )
                fee.total_amount = Decimal('70000.00')
                fee.paid_amount += dec_payment
                fee.payment_method = payment_method
                fee.payment_date = timezone.now()
                fee.save()
                messages.success(request, f"Fee payment of ₹{dec_payment:,.2f} recorded for {student.full_name} ({student.student_id}) in {semester}! Remaining Balance Due: ₹{fee.remaining_due:,.2f}.")
                stream_code = student.department.code if student.department else 'ECE'
                return redirect(f"{reverse('core:fee_list')}?fee_stream={stream_code}&fee_year={student.year}&fee_sem={semester}")
        else:
            messages.error(request, "Error recording fee payment. Please fill in all required fields.")
            return redirect('core:fee_list')

    fee_stream = request.GET.get('fee_stream', 'ECE').strip()
    fee_year = request.GET.get('fee_year', 'I').strip()
    fee_sem = request.GET.get('fee_sem', '').strip()
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    fee_results = get_fee_collection_matrix(
        stream_code=fee_stream,
        year=fee_year,
        semester=fee_sem or None,
        search_query=search_query,
        status_filter=status_filter
    )

    active_students = StudentProfile.objects.filter(status='Active').select_related('department').order_by('student_id')
    students_for_modal = [
        {
            'id': sp.id,
            'roll_no': sp.student_id,
            'full_name': sp.full_name,
            'stream': sp.department.code if sp.department else 'ECE',
            'year': sp.year or 'I',
        }
        for sp in active_students
    ]

    all_fees_lookup = {
        f"{f.student_id}_{f.semester}": {
            'total': float(f.total_amount),
            'paid': float(f.paid_amount),
            'due': float(f.remaining_due)
        }
        for f in StudentFee.objects.all().select_related('student')
    }

    return render(request, 'core/fees/fee_list.html', {
        'fee_results': fee_results,
        'fee_stream': fee_stream,
        'fee_year': fee_year,
        'fee_sem': fee_results['semester'],
        'search_query': search_query,
        'selected_status': status_filter,
        'status_choices': StudentFee.STATUS_CHOICES,
        'fee_students_json': json.dumps(students_for_modal),
        'fee_lookup_json': json.dumps(all_fees_lookup),
    })


@admin_required
def fee_create_view(request):
    if request.method == 'POST':
        form = StudentFeeForm(request.POST)
        if form.is_valid():
            fee = form.save()
            messages.success(request, f"Fee invoice '{fee.title}' issued successfully!")
            return redirect('core:fee_list')
    else:
        form = StudentFeeForm()

    return render(request, 'core/fees/fee_form.html', {'form': form, 'title': 'Create Student Fee Invoice'})


@admin_required
def fee_pay_view(request, pk):
    fee = get_object_or_404(StudentFee, pk=pk)
    if request.method == 'POST':
        form = RecordPaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['payment_amount']
            method = form.cleaned_data['payment_method']
            fee.paid_amount += amount
            fee.payment_method = method
            fee.payment_date = datetime.now()
            fee.save()
            messages.success(request, f"Payment of ₹{amount} recorded via {method}. New status: {fee.get_status_display()}.")
            return redirect('core:fee_list')
    else:
        form = RecordPaymentForm(initial={'payment_amount': fee.remaining_due})

    return render(request, 'core/fees/record_payment.html', {'fee': fee, 'form': form})


# ==========================================
# ACADEMIC CORE & REPORTS VIEWS
# ==========================================

@login_required
def department_list_view(request):
    departments = Department.objects.all().select_related('head_of_department')
    return render(request, 'core/departments/department_list.html', {'departments': departments})

@admin_required
def department_create_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Branch '{dept.name}' ({dept.code}) created successfully!")
            return redirect('core:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'core/departments/department_form.html', {'form': form, 'title': 'Add Engineering Branch'})

@admin_required
def department_edit_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{dept.name}' updated successfully.")
            return redirect('core:department_list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'core/departments/department_form.html', {'form': form, 'title': f"Edit Branch - {dept.code}", 'department': dept})

@login_required
def course_list_view(request):
    courses = Course.objects.all().select_related('department')
    return render(request, 'core/courses/course_list.html', {'courses': courses})

@admin_required
def course_create_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.name}' created successfully!")
            return redirect('core:course_list')
    else:
        form = CourseForm()
    return render(request, 'core/courses/course_form.html', {'form': form, 'title': 'Add B.Tech Course Program'})

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
    return render(request, 'core/courses/course_form.html', {'form': form, 'title': f"Edit Course - {course.code}", 'course': course})

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
    return render(request, 'core/academic/academic_years.html', {'years': years, 'form': form})

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
    return render(request, 'core/academic/semesters.html', {'semesters': semesters, 'form': form})

@login_required
def subject_list_view(request):
    subjects = Subject.objects.all().select_related('course', 'assigned_teacher')
    if request.method == 'POST' and request.user.is_admin_user:
        form = SubjectForm(request.POST)
        if form.is_valid():
            sub = form.save()
            messages.success(request, f"Subject '{sub.name}' added successfully!")
            return redirect('core:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'core/subjects/subject_list.html', {'subjects': subjects, 'form': form})

@login_required
def reports_view(request):
    students = StudentProfile.objects.all().select_related('course', 'department')
    teachers = TeacherProfile.objects.all().select_related('department')
    dept_stats = Department.objects.annotate(student_count=Count('studentprofile')).filter(is_active=True)
    course_stats = Course.objects.annotate(student_count=Count('studentprofile')).filter(is_active=True)

    return render(request, 'core/reports/reports.html', {
        'students_count': students.count(),
        'teachers_count': teachers.count(),
        'dept_stats': dept_stats,
        'course_stats': course_stats,
        'recent_students': students.order_by('-created_at')[:10],
    })
