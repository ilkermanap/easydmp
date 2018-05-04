"""
Django settings for easydmp project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
updir = os.path.dirname
pathjoin = os.path.join

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
SETTINGS_DIR = updir(os.path.abspath(__file__))
SITE_DIR = updir(SETTINGS_DIR)
BASE_DIR = updir(updir(updir(SITE_DIR)))

# For production, you probably want to change all variables that use BASE_DIR


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # For flatpages
    'django.contrib.flatpages',

    'crispy_forms',
    'rest_framework',
    'django_select2',
    'django_filters',
    'rest_framework_filters',

    'easydmp.auth.apps.EasyDMPAuthConfig',
    'flow',
    'easydmp.dmpt',
    'easydmp.plan',
    'easydmp.invitation',
    'easydmp.eestore',
]

SITE_ID = 1 # For flatpages

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'easydmp.site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            pathjoin(SITE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'easydmp.site.wsgi.application'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    pathjoin(SITE_DIR, 'static'),
]

STATIC_ROOT = pathjoin(BASE_DIR, 'collected_static_files')

# Auth

AUTH_USER_MODEL = 'easydmp_auth.User'

LOGIN_URL = 'login-selector'
LOGIN_REDIRECT_URL = '/plan/'

# REST API

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v1',
    'DEFAULT_FILTER_BACKENDS': ('rest_framework_filters.backends.DjangoFilterBackend',),
}

# PSA

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'email']
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/plan/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = SOCIAL_AUTH_LOGIN_REDIRECT_URL
