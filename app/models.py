from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ============ ប្រវត្តិអ្នកប្រើប្រាស់ ============
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'គ្រូ'),
        ('student', 'សិស្ស'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    @property
    def is_teacher(self):
        return self.role in ['teacher', 'admin']
    
    @property
    def is_admin(self):
        return self.role == 'admin'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# ============ មុខវិជ្ជា ============
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name


# ============ សំណួរ ============
class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'ងាយ'),
        ('medium', 'មធ្យម'),
        ('hard', 'ពិបាក'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    points = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.question_text[:50]


# ============ ការប្រឡង ============
class Exam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, related_name='exams')
    duration_minutes = models.IntegerField(default=30)
    total_marks = models.IntegerField(default=0)
    pass_percentage = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    show_answers_after_exam = models.BooleanField(default=True, verbose_name="អនុញ្ញាតឱ្យមើលចម្លើយក្រោយប្រឡង")
    max_attempts = models.IntegerField(default=1, verbose_name="ចំនួនដងអតិបរមាដែលអាចប្រឡងបាន")
    assigned_students = models.ManyToManyField(User, related_name='assigned_exams', blank=True, verbose_name="សិស្សដែលត្រូវចូលរួម")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


# ============ ការប្រឡងរបស់សិស្ស ============
class ExamAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'កំពុងប្រឡង'),
        ('completed', 'បានបញ្ចប់'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    is_passed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"


# ============ ចម្លើយរបស់សិស្ស ============
class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.id}"


# ============ ប្រព័ន្ធជូនដំណឹង (Notifications) ============
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(verbose_name="សារជូនដំណឹង")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="តំណភ្ជាប់")
    is_read = models.BooleanField(default=False, verbose_name="បានអានហើយឬនៅ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"


# ============ ការកំណត់ប្រព័ន្ធ (System Settings) ============
class SystemSettings(models.Model):
    app_name = models.CharField(max_length=100, default="LMS MCQ System", verbose_name="ឈ្មោះកម្មវិធី")
    announcement = models.TextField(blank=True, null=True, verbose_name="សារជូនដំណឹងទូទៅ")
    
    # ⬇️ Field ថ្មីៗសម្រាប់ Branding ⬇️
    logo = models.ImageField(upload_to='branding/', blank=True, null=True, verbose_name="Logo កម្មវិធី")
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True, verbose_name="Favicon (រូបតូចលើ Tab)")
    primary_color = models.CharField(max_length=7, default="#0d6efd", verbose_name="ពណ៌ចម្បង (Hex Code)")
    login_background = models.ImageField(upload_to='branding/', blank=True, null=True, verbose_name="រូបភាពផ្ទៃខាងក្រោយទំព័រ Login")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ការកំណត់ប្រព័ន្ធ"
        verbose_name_plural = "ការកំណត់ប្រព័ន្ធ"

    def __str__(self):
        return "ការកំណត់ប្រព័ន្ធ"