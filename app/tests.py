from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Subject, Question, Exam, ExamAttempt, StudentAnswer
from django.utils import timezone

class LMSTestCase(TestCase):
    def setUp(self):
        """រៀបចំទិន្នន័យសាកល្បងមុនពេលរត់ការតេស្តនីមួយៗ"""
        # ១. បង្កើតគណនីគ្រូ
        self.teacher = User.objects.create_user(username='teacher1', password='Password123')
        self.teacher.profile.role = 'teacher'
        self.teacher.profile.save()

        # ២. បង្កើតគណនីសិស្ស
        self.student = User.objects.create_user(username='student1', password='Password123')
        self.student.profile.role = 'student'
        self.student.profile.save()

        # ៣. បង្កើតមុខវិជ្ជា
        self.subject = Subject.objects.create(name='គណិតវិទ្យា', code='MATH01')

        # ៤. បង្កើតសំណួរ
        self.question = Question.objects.create(
            subject=self.subject,
            question_text='តើ 2 + 2 ស្មើប៉ុន្មាន?',
            option_a='3', option_b='4', option_c='5', option_d='6',
            correct_answer='B',
            points=1,
            created_by=self.teacher
        )

        # ៥. បង្កើតការប្រឡង
        self.exam = Exam.objects.create(
            title='ការប្រឡងគណិតវិទ្យា',
            subject=self.subject,
            duration_minutes=30,
            pass_percentage=50,
            max_attempts=1,
            created_by=self.teacher
        )
        self.exam.questions.add(self.question)
        self.exam.assigned_students.add(self.student)
        self.exam.save()
        
        # កំណត់ពិន្ទុសរុបឱ្យច្បាស់លាស់ ដើម្បីកុំឱ្យ Error 0.0
        self.exam.total_marks = self.question.points
        self.exam.save()

        # បង្កើត Client សម្រាប់ធ្វើតេស្ត
        self.client = Client()

    # ==========================================
    # ១. ការតេស្តសុវត្ថិភាព និងសិទ្ធិ (Security & Permissions)
    # ==========================================

    def test_student_cannot_access_teacher_dashboard(self):
        """សិស្សមិនអាចចូលទំព័របញ្ចូលសំណួរបានទេ"""
        self.client.login(username='student1', password='Password123')
        url = reverse('add_question')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_teacher_cannot_access_admin(self):
        """គ្រូធម្មតាមិនអាចចូលទំព័រ Admin បានទេ"""
        self.client.login(username='teacher1', password='Password123')
        response = self.client.get('/secret-admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url or '/secret-admin/login/' in response.url)

    def test_unauthenticated_user_redirected_to_login(self):
        """អ្នកដែលមិនទាន់ Login មិនអាចចូលទំព័រ Dashboard បានទេ"""
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    # ==========================================
    # ២. ការតេស្តការប្រឡង (Exam Workflow)
    # ==========================================

    def test_exam_assignment(self):
        """សិស្សដែលត្រូវបានអញ្ជើញគួរតែឃើញការប្រឡង"""
        self.client.login(username='student1', password='Password123')
        url = reverse('exam_list')
        response = self.client.get(url)
        self.assertContains(response, 'ការប្រឡងគណិតវិទ្យា')

    def test_submit_exam_and_calculate_score(self):
        """តេស្តការប្រឡង និងការគណនាពិន្ទុស្វ័យប្រវត្តិ"""
        self.client.login(username='student1', password='Password123')
        
        url = reverse('take_exam', args=[self.exam.id])
        
        data = {
            f'question_{self.question.id}': 'B'
        }
        
        response = self.client.post(url, data)
        
        attempt = ExamAttempt.objects.filter(student=self.student, exam=self.exam).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score, 1) 
        self.assertEqual(attempt.percentage, 100.0)
        self.assertTrue(attempt.is_passed)

    def test_max_attempts_limit(self):
        """សិស្សមិនអាចប្រឡងលើសពីចំនួនដងដែលបានកំណត់បានទេ"""
        self.client.login(username='student1', password='Password123')
        
        # បង្កើត Attempt ដែលបានបញ្ចប់រួចហើយ
        ExamAttempt.objects.create(
            student=self.student, 
            exam=self.exam, 
            status='completed',
            score=1,
            percentage=100,
            is_passed=True
        )
        
        url = reverse('take_exam', args=[self.exam.id])
        response = self.client.get(url, follow=True)
        
        # ពិនិត្យមើលថាតើវាបានបញ្ជូនត្រឡប់ទៅបញ្ជីប្រឡងវិញឬអត់
        self.assertRedirects(response, reverse('exam_list'))