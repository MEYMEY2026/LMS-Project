from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.contrib import messages
from .models import UserProfile, Subject, Question, Exam, ExamAttempt, StudentAnswer, Notification, SystemSettings
from django.contrib.auth.models import User

# កំណត់ឈ្មោះផ្ទាំង Admin ឱ្យស្អាត
admin.site.site_header = "ប្រព័ន្ធគ្រប់គ្រង LMS MCQ"
admin.site.site_title = "LMS Admin"
admin.site.index_title = "ផ្ទាំងគ្រប់គ្រងទិន្នន័យ"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'subject', 'correct_answer', 'difficulty', 'points', 'created_by')
    list_filter = ('subject', 'difficulty', 'correct_answer')
    search_fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d')
    fieldsets = (
        ('ព័ត៌មានទូទៅ', {
            'fields': ('subject', 'question_text', 'difficulty', 'points', 'created_by')
        }),
        ('ជម្រើសចម្លើយ', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
    )
    def question_text_short(self, obj):
        return obj.question_text[:60] + "..." if len(obj.question_text) > 60 else obj.question_text
    question_text_short.short_description = 'សំណួរ'

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'duration_minutes', 'total_marks', 'created_by', 'is_active')
    list_filter = ('subject', 'is_active', 'created_by')
    search_fields = ('title',)
    filter_horizontal = ('questions',)

@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'percentage', 'is_passed', 'status', 'completed_at')
    list_filter = ('status', 'is_passed', 'exam')
    search_fields = ('student__username', 'exam__title')

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('attempt__student__username', 'question__question_text')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_short', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    def message_short(self, obj):
        return obj.message[:50]
    message_short.short_description = 'សារ'

# បង្កើតទំព័រកំណត់ពិសេសនៅក្នុង Admin
class SystemSettingsAdmin(admin.ModelAdmin):
    change_list_template = "admin/system_settings_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update-settings/', self.admin_site.admin_view(self.update_settings), name='update-settings'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        settings_obj, created = SystemSettings.objects.get_or_create(id=1)
        extra_context = extra_context or {}
        extra_context['settings_obj'] = settings_obj
        return super().changelist_view(request, extra_context=extra_context)

    def update_settings(self, request):
        if request.method == 'POST':
            app_name = request.POST.get('app_name')
            announcement = request.POST.get('announcement')
            send_notification = request.POST.get('send_notification') == 'on'

            settings_obj, _ = SystemSettings.objects.get_or_create(id=1)
            settings_obj.app_name = app_name
            settings_obj.announcement = announcement
            settings_obj.save()

            if send_notification and announcement:
                users = User.objects.all()
                for user in users:
                    Notification.objects.create(
                        user=user,
                        message=f"📢 សេចក្តីជូនដំណឹងថ្មី: {announcement}",
                        link="/dashboard/"
                    )
                messages.success(request, 'បានរក្សាទុកការកំណត់ និងផ្ញើសារជូនដំណឹងដល់អ្នកប្រើទាំងអស់ដោយជោគជ័យ! ✅')
            else:
                messages.success(request, 'បានរក្សាទុកការកំណត់ដោយជោគជ័យ! ✅')
            
            return redirect('admin:app_systemsettings_changelist')

        return redirect('admin:app_systemsettings_changelist')

admin.site.register(SystemSettings, SystemSettingsAdmin)