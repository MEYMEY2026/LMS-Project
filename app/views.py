from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count
import random
import csv
import openpyxl

# Import Models ទាំងអស់ពី app
from .models import Subject, Question, Exam, ExamAttempt, StudentAnswer, Notification, SystemSettings


# ==========================================
# ១. មុខងារទូទៅ (Authentication)
# ==========================================

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'សូមស្វាគមន៍ {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'ឈ្មោះ ឬលេខសម្ងាត់មិនត្រឹមត្រូវ!')
            
    return render(request, 'login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'ឈ្មោះនេះមានអ្នកប្រើរួចហើយ!')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.profile.role = 'student'
            user.profile.save()
            
            messages.success(request, 'ចុះឈ្មោះបានជោគជ័យ! សូមចូលប្រើប្រាស់។')
            return redirect('login')
            
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # ១. ទាញយក Notifications សម្រាប់អ្នកប្រើ
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    # ២. គណនាស្ថិតិសម្រាប់បង្ហាញនៅលើ Dashboard
    total_students = User.objects.filter(profile__role='student').count()
    total_questions = Question.objects.count()
    total_exams = Exam.objects.count()
    completed_exams = ExamAttempt.objects.filter(status='completed').count()
    
    context = {
        'unread_notifications': unread_notifications,
        'total_students': total_students,
        'total_questions': total_questions,
        'total_exams': total_exams,
        'completed_exams': completed_exams,
    }
    
    return render(request, 'dashboard.html', context)


# ==========================================
# ២. មុខងារសម្រាប់គ្រូបង្រៀន (Teacher)
# ==========================================

@login_required
def manage_subjects(request):
    if not request.user.profile.is_teacher:
        messages.error(request, 'អ្នកមិនមានសិទ្ធិចូលទំព័រនេះទេ!')
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        
        if not name or not code:
            messages.error(request, 'សូមបំពេញឈ្មោះ និងកូដមុខវិជ្ជាឱ្យបានត្រឹមត្រូវ!')
        elif Subject.objects.filter(code=code).exists():
            messages.error(request, 'កូដមុខវិជ្ជានេះមានរួចហើយ!')
        else:
            Subject.objects.create(name=name, code=code.upper())
            messages.success(request, f'បង្កើតមុខវិជ្ជា "{name}" បានជោគជ័យ! ✅')
            return redirect('manage_subjects')

    subjects = Subject.objects.all().order_by('name')
    return render(request, 'manage_subjects.html', {'subjects': subjects})


@login_required
def add_question(request):
    if not request.user.profile.is_teacher:
        messages.error(request, 'អ្នកមិនមានសិទ្ធិចូលទំព័រនេះទេ!')
        return redirect('dashboard')
        
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        question_text = request.POST.get('question_text')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c')
        option_d = request.POST.get('option_d')
        correct_answer = request.POST.get('correct_answer')
        
        subject = get_object_or_404(Subject, id=subject_id)
        
        Question.objects.create(
            subject=subject,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            created_by=request.user
        )
        messages.success(request, 'បញ្ចូលសំណួរបានជោគជ័យ! ✅')
        return redirect('question_list')
        
    subjects = Subject.objects.all()
    return render(request, 'add_question.html', {'subjects': subjects})


@login_required
def question_list(request):
    if not request.user.profile.is_teacher:
        return redirect('dashboard')
        
    my_questions = Question.objects.filter(created_by=request.user).order_by('subject__name', '-id')
    other_stats = Subject.objects.annotate(
        total_questions=Count('questions')
    ).filter(total_questions__gt=0).order_by('name')
    subjects = Subject.objects.all()
    
    return render(request, 'question_list.html', {
        'my_questions': my_questions,
        'other_stats': other_stats,
        'subjects': subjects
    })


@login_required
def create_exam(request):
    if not request.user.profile.is_teacher:
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        duration = request.POST.get('duration')
        pass_percentage = request.POST.get('pass_percentage', 50)
        max_attempts = request.POST.get('max_attempts', 1)
        question_ids = request.POST.getlist('questions')
        student_ids = request.POST.getlist('students')
        
        show_answers = request.POST.get('show_answers_after_exam') == 'on'
        
        if not question_ids:
            messages.error(request, 'សូមជ្រើសរើសសំណួរយ៉ាងតិច ១!')
            return redirect('create_exam')
            
        subject, _ = Subject.objects.get_or_create(name="ទូទៅ", defaults={'code': 'GEN'})
        
        exam = Exam.objects.create(
            title=title,
            subject=subject,
            duration_minutes=int(duration),
            pass_percentage=int(pass_percentage),
            max_attempts=int(max_attempts),
            show_answers_after_exam=show_answers,
            created_by=request.user
        )
        
        questions = Question.objects.filter(id__in=question_ids)
        exam.questions.set(questions)
        
        if student_ids:
            students = User.objects.filter(id__in=student_ids)
            exam.assigned_students.set(students)
            
            for student in students:
                Notification.objects.create(
                    user=student,
                    message=f"អ្នកត្រូវបានអញ្ជើញឱ្យចូលរួមការប្រឡង: {exam.title}",
                    link=f"/exams/{exam.id}/take/"
                )
            
        exam.save()
        
        messages.success(request, 'បង្កើតការប្រឡង និងអញ្ជើញសិស្សបានជោគជ័យ! ✅')
        return redirect('dashboard')
        
    questions = Question.objects.filter(created_by=request.user).order_by('subject__name')
    subjects = Subject.objects.all()
    students = User.objects.filter(profile__role='student').order_by('username')
    
    return render(request, 'create_exam.html', {
        'questions': questions,
        'subjects': subjects,
        'students': students,
    })


# ==========================================
# ៣. មុខងារសម្រាប់សិស្ស (Student Exam)
# ==========================================

@login_required
def exam_list(request):
    if request.user.profile.is_teacher:
        exams = Exam.objects.filter(is_active=True)
        return render(request, 'exam_list.html', {'exams': exams})
    else:
        exams = Exam.objects.filter(is_active=True, assigned_students=request.user)
        
        exam_data = []
        for exam in exams:
            attempt_count = ExamAttempt.objects.filter(
                student=request.user, 
                exam=exam, 
                status='completed'
            ).count()
            
            exam_data.append({
                'exam': exam,
                'has_attempted': attempt_count >= exam.max_attempts
            })
            
        return render(request, 'exam_list.html', {'exam_data': exam_data})


@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not request.user.profile.is_teacher:
        if request.user not in exam.assigned_students.all():
            messages.error(request, 'អ្នកមិនត្រូវបានអញ្ជើញឱ្យចូលប្រឡងនេះទេ!')
            return redirect('exam_list')

    attempts_count = ExamAttempt.objects.filter(
        student=request.user, 
        exam=exam, 
        status='completed'
    ).count()
    
    if attempts_count >= exam.max_attempts:
        messages.error(request, f'អ្នកបានប្រឡងអស់ {exam.max_attempts} ដងហើយ! មិនអាចប្រឡងបន្ថែមបានទេ។')
        return redirect('exam_list')
    
    attempt, created = ExamAttempt.objects.get_or_create(
        student=request.user, 
        exam=exam,
        status='in_progress'
    )
    
    if request.method == 'POST':
        score = 0
        for question in exam.questions.all():
            selected = request.POST.get(f'question_{question.id}')
            
            if selected:
                is_correct = (selected == question.correct_answer)
                
                StudentAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected,
                    is_correct=is_correct
                )
                
                if is_correct:
                    score += question.points
        
        attempt.score = score
        attempt.percentage = (score / exam.total_marks * 100) if exam.total_marks > 0 else 0
        attempt.is_passed = attempt.percentage >= exam.pass_percentage
        attempt.status = 'completed'
        attempt.completed_at = timezone.now()
        attempt.save()
        
        return redirect('exam_result', attempt_id=attempt.id)
    
    questions = list(exam.questions.all())
    random.shuffle(questions)
    
    return render(request, 'take_exam.html', {
        'exam': exam,
        'questions': questions,
        'attempt': attempt
    })


@login_required
def exam_result(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    
    if attempt.student != request.user and not request.user.profile.is_teacher:
        return redirect('dashboard')
        
    answers = attempt.answers.all()
    
    return render(request, 'result.html', {
        'attempt': attempt,
        'answers': answers
    })


# ==========================================
# ៤. មុខងារមើលលទ្ធផល (Results)
# ==========================================

@login_required
def student_results(request):
    if request.user.profile.is_teacher:
        return redirect('dashboard')
        
    attempts = ExamAttempt.objects.filter(
        student=request.user, 
        status='completed'
    ).order_by('-completed_at')
    
    return render(request, 'student_results.html', {'attempts': attempts})


@login_required
def teacher_results(request):
    if not request.user.profile.is_teacher:
        return redirect('dashboard')
        
    if request.user.profile.is_admin:
        attempts = ExamAttempt.objects.filter(status='completed').order_by('-completed_at')
    else:
        attempts = ExamAttempt.objects.filter(
            exam__created_by=request.user, 
            status='completed'
        ).order_by('-completed_at')
        
    return render(request, 'teacher_results.html', {'attempts': attempts})


# ==========================================
# ៥. មុខងារ Import សំណួរ (Excel/CSV)
# ==========================================

@login_required
def import_questions(request):
    if not request.user.profile.is_teacher:
        messages.error(request, 'អ្នកមិនមានសិទ្ធិចូលទំព័រនេះទេ!')
        return redirect('dashboard')

    subjects = Subject.objects.all()

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_name = file.name.lower()
        subject_id = request.POST.get('subject')
        
        if not subject_id:
            messages.error(request, 'សូមជ្រើសរើសមុខវិជ្ជាមុនពេល Upload File!')
            return redirect('import_questions')
            
        subject = get_object_or_404(Subject, id=subject_id)
        
        success_count = 0
        error_count = 0

        try:
            if file_name.endswith('.csv'):
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                next(reader)
                for row in reader:
                    if len(row) >= 6: 
                        Question.objects.create(
                            subject=subject,
                            question_text=row[0],
                            option_a=row[1],
                            option_b=row[2],
                            option_c=row[3],
                            option_d=row[4],
                            correct_answer=row[5].upper().strip(),
                            created_by=request.user
                        )
                        success_count += 1
                    else:
                        error_count += 1

            elif file_name.endswith(('.xlsx', '.xls')):
                wb = openpyxl.load_workbook(file)
                sheet = wb.active
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if row[0]:
                        try:
                            Question.objects.create(
                                subject=subject,
                                question_text=str(row[0]),
                                option_a=str(row[1]),
                                option_b=str(row[2]),
                                option_c=str(row[3]),
                                option_d=str(row[4]),
                                correct_answer=str(row[5]).upper().strip(),
                                created_by=request.user
                            )
                            success_count += 1
                        except Exception:
                            error_count += 1
            else:
                messages.error(request, 'សូមផ្ទុកឡើងតែ File .xlsx, .xls ឬ .csv ប៉ុណ្ណោះ!')
                return redirect('import_questions')

            messages.success(request, f'បញ្ចូលបានជោគជ័យ {success_count} សំណួរ ទៅក្នុងមុខវិជ្ជា {subject.name}! (បរាជ័យ {error_count})')
            return redirect('question_list')

        except Exception as e:
            messages.error(request, f'មានបញ្ហាក្នុងការអាន File: {str(e)}')
            return redirect('import_questions')

    return render(request, 'import_questions.html', {'subjects': subjects})


@login_required
def download_template(request):
    if not request.user.profile.is_teacher:
        return redirect('dashboard')
        
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Questions"
    
    headers = ['សំណួរ', 'ជម្រើស A', 'ជម្រើស B', 'ជម្រើស C', 'ជម្រើស D', 'ចម្លើយត្រូវ (A/B/C/D)']
    ws.append(headers)
    ws.append(['តើរាជធានីកម្ពុជាឈ្មោះអ្វី?', 'សៀមរាប', 'ភ្នំពេញ', 'កំពត', 'បាត់ដំបង', 'B'])
    ws.append(['តើ 5 x 3 = ?', '10', '12', '15', '20', 'C'])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="question_template.xlsx"'
    wb.save(response)
    return response


# ==========================================
# ៦. មុខងារគ្រប់គ្រង Notifications
# ==========================================

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


# ==========================================
# ៧. មុខងារគ្រប់គ្រងព័ត៌មានផ្ទាល់ខ្លួន (Profile)
# ==========================================

@login_required
def profile_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        user = request.user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, 'ព័ត៌មានផ្ទាល់ខ្លួនត្រូវបានធ្វើបច្ចុប្បន្នភាពដោយជោគជ័យ! ✅')
        return redirect('profile')
        
    return render(request, 'profile.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'លេខសម្ងាត់ត្រូវបានប្តូរដោយជោគជ័យ! ✅')
            return redirect('profile')
        else:
            messages.error(request, 'សូមពិនិត្យលេខសម្ងាត់ចាស់ ឬលេខសម្ងាត់ថ្មីម្តងទៀត!')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'change_password.html', {'form': form})