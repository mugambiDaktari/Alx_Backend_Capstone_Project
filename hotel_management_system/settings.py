from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-l3a58&6b3zw%8!jp7e7(%(m$%jafj(l*&886+gr$qd-a%)fm#q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hotel_app',
    'rest_framework',
    'rest_framework_simplejwt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hotel_management_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hotel_management_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# JWT Settings (Optional)
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  # Token expires in 1 day
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # Refresh token lasts 7 days
    "ROTATE_REFRESH_TOKENS": True,  #  each time the user refreshes their token, they receive a new refresh token along with a new access token.
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),  # Authorization: Bearer <token>
}
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Define the directory where static files will be collected
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# URLs for static and media files
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Directory where user-uploaded files will be stored
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Ensure static files are collected
STATICFILES_DIRS = [os.path.join(BASE_DIR, "hotel_app", "static")]



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'hotel_app.User'
LOGIN_REDIRECT_URL = 'homepage'  # Redirects user to homepage after login
LOGOUT_REDIRECT_URL = 'login'  # Redirect login page after logout

#  security against XSS, clickjacking, and MIME attacks
SECURE_BROWSER_XSS_FILTER = True  # Protects against XSS attacks
X_FRAME_OPTIONS = "DENY"  # Prevents clickjacking attacks
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevents MIME-type sniffing

SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
SESSION_COOKIE_SECURE = True  # Secure session cookies
CSRF_COOKIE_SECURE = True  # Secure CSRF cookies

# HTTP Strict Transport Security (HSTS) settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_REFERRER_POLICY = "same-origin"  # Referrer policy to control the information sent in the Referer header

CSRF_COOKIE_SECURE = True  # Only send CSRF cookie over HTTPS
CSRF_USE_SESSIONS = True  # Store CSRF token in sessions instead of cookies

X_FRAME_OPTIONS = "DENY"  # Prevents clickjacking attacks by not allowing the site to be displayed in a frame or iframe 