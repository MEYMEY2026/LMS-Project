"""
Django settings for config project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4+66u_&rj__!@1=2fhj@b=1t7o%$d+w95u(q25^qs^poxy*hns'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# អនុញ្ញាតឱ្យចូលប្រើតាម Localhost និង IP ក្នុងបណ្តាញ
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'lmsmcq.pythonanywhere.com']

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # ត្រូវតែដាក់នៅខាងលើគេបំផុត!
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'rest_framework.authtoken',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ⬅️ បន្ថែម WhiteNoise សម្រាប់ Static Files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # 'app.middleware.AdminIPRestrictionMiddleware', # បើកវិញពេលចង់កំណត់ IP សម្រាប់ Admin
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'app' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.notifications_processor',
                'app.context_processors.app_settings_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'km'
TIME_ZONE = 'Asia/Phnom_Penh'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'app' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ការកំណត់សម្រាប់ WhiteNoise (ដើម្បីឱ្យ CSS/JS ដំណើរការពេល DEBUG=False)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# កំណត់សម្រាប់ការ Login
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

# Email
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

# ==========================================
# CUSTOM SETTINGS
# ==========================================

# សម្រាប់ REST API
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# សម្រាប់ Telegram Bot
TELEGRAM_BOT_TOKEN = ''
SITE_URL = 'http://localhost:8000'

# ==========================================
# ការកំណត់ Jazzmin (Admin UI)
# ==========================================
JAZZMIN_SETTINGS = {
    # ចំណងជើងផ្ទាំង
    "site_title": "LMS MCQ Admin",
    "site_header": "ប្រព័ន្ធគ្រប់គ្រង LMS",
    "site_brand": "LMS System",
    "welcome_sign": "សូមស្វាគមន៍មកកាន់ផ្ទាំងគ្រប់គ្រង",
    
    # បង្ហាញប្រអប់ស្វែងរកនៅខាងលើ
    "search_model": ["auth.User", "app.Question", "app.Exam"],
    
    # បង្ហាញ Menu ខាងលើ
    "topmenu_links": [
        {"name": "ទំព័រដើម",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "គេហទំព័រ", "url": "/", "new_window": True},
    ],
    
    # រូបតំណាងសម្រាប់ Menu
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "app.Question": "fas fa-question-circle",
        "app.Exam": "fas fa-file-alt",
        "app.UserProfile": "fas fa-id-card",
        "app.ExamAttempt": "fas fa-check-circle",
        "app.SystemSettings": "fas fa-cogs",
    },
    
    # ភ្ជាប់ CSS ផ្ទាល់ខ្លួន (ប្រសិនបើអ្នកបានបង្កើតវា)
    "custom_css": "css/admin_custom.css",
    
    # ភាសា
    "language_chooser": False,
}

# កំណត់ពណ៌ និងម៉ូត
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly", # ប្រើ Theme ស្អាតៗ
    "navbar": "navbar-dark navbar-primary", # ពណ៌ Navy Blue
    "sidebar": "sidebar-dark-primary", # ពណ៌ Sidebar ខ្មៅ/ខៀវចាស់
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}