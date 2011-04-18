# coding: utf-8

# Django settings for openresources test project.
# Requires Django >= 1.2

import os

ROOT_PATH = os.path.dirname(__file__)

TEMPLATE_DEBUG = DEBUG = True

MANAGERS = ADMINS = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testproject.db',
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True
LANGUAGES = (
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
)

MEDIA_ROOT = ''
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
SERVE_STATIC = True

AUTH_PROFILE_MODULE = 'openresources.UserProfile'

SECRET_KEY = 'rx62k39-m+c%gh78r+nau0x$j_89y*o@d4)+qu*ey^5ktg72a_'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates'),
)

INSTALLED_APPS = [
    'openresources',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
]

try:
    import south
    INSTALLED_APPS.append('south')
except ImportError:
    # south not installed
    pass
