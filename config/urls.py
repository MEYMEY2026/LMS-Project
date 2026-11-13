from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

# បង្កើត Custom Admin Site ដើម្បីកំណត់ឱ្យវាបញ្ជូនទៅ Login ធម្មតា បើគ្មានសិទ្ធិ
class CustomAdminSite(admin.AdminSite):
    def login(self, request, extra_context=None):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().login(request, extra_context)

# ជំនួស Admin Site ចាស់ដោយ Custom Admin Site ថ្មី
admin.site.__class__ = CustomAdminSite

urlpatterns = [
    path('secret-admin/', admin.site.urls),  # ⬅️ ប្តូរឈ្មោះពី admin ទៅ secret-admin
    path('', include('app.urls')), # ភ្ជាប់ទៅកាន់ app
]

# សម្រាប់បង្ហាញរូបភាព និង File
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)