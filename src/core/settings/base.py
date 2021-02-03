from os.path import join

from . import env, BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')
API_HOST = env('API_HOST')
API_PORT = env('API_PORT')
CUSTON_DOMAIN = env('CUSTOM_DOMAIN')
UI_HOST = env('UI_HOST')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[API_HOST, 'api'])

# Application definition
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)
THIRD_PARTY_APPS = (
    'rest_framework',
    'corsheaders',
    'django_crontab',
    'django_filters',
    'bandit',
    'django_nose'
)
LOCAL_APPS = (
    'api',
    'api_base',
    'api_user',
    'api_admin',
    'api_team',
    'api_workday',
    'api_providers',
    'api_lunch',
    'api_user_lunch',
    'api_event',
    'api_company',
)
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "api_user.User"

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Config django-cors lib
CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', default=False)
CORS_ORIGIN_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', default=[
    'http://127.0.0.1:8001',
    'http://localhost:8001',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://192.168.3.44:8080'
])
CORS_ORIGIN_REGEX_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', default=[])
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Config Django Rest framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.authentications.APIAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.CustomPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Testing
<<<<<<< HEAD
# # Use nose to run all tests
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
#
# # Tell nose to measure coverage on the 'foo' and 'bar' apps
# NOSE_ARGS = [
#     '--with-coverage',
#     '--cover-package=api_user_lunch,api_lunch, api_workday, api_user',
# ]
=======
# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=api_user_lunch,api_lunch, api_workday, api_user',
]
>>>>>>> 9f46d291ffae186729005f49d074dd9d03ca1728

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database

def db_config(prefix='', test=None):
    if test is None:
        test = {}
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': prefix + env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASS'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'TEST': test,
        'OPTIONS': {
            'init_command': 'SET GLOBAL max_connections = 100000',
            'charset': 'utf8mb4'
        }
    }


# Backup Database
REPLICATION_DB_ALIAS = 'replication'
REPLICATION_PREFIX = env('REPLICATION_DB_PREFIX', default='')

DATABASES = {
    'default': db_config(),
    'tests': db_config('', {'MIRROR': 'default'}),
    REPLICATION_DB_ALIAS: db_config(REPLICATION_PREFIX)
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_L10N = True
USE_TZ = False

# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
# MEDIA related settings
MEDIA_ROOT = join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

MEDIA_IMAGE = f'{CUSTON_DOMAIN}'

# EMAIL related settings
GRANTED_MAIL = [
    env('DEV_MAIL')
]

BANDIT_WHITELIST = GRANTED_MAIL
BANDIT_EMAIL = ''

URL_WEB_INTERNAL = env("WEB_INTERNAL", default='paradox.ai')

CALENDAR_ID = env('CALENDAR_ID')

# SLACK
SLACK_VERIFICATION_TOKEN = env('SLACK_VERIFICATION_TOKEN')
OAUTH_ACCESS_TOKEN = env('SLACK_OAUTH_ACCESS_TOKEN')
BOT_USER_ACCESS_TOKEN = env('SLACK_BOT_USER_ACCESS_TOKEN')
CLIENT_ID = env('SLACK_CLIENT_ID')
CLIENT_SECRET = env('SLACK_CLIENT_SECRET')
CHANNEL = env('CHANNEL')
CHANNEL_LEAVE_NOTICE = env('CHANNEL_LEAVE_NOTICE')
LINK_EVENT_SYSTEM = env('LINK_EVENT_SYSTEM')

CRONJOBS = [
    ('* 10 * * 5', 'api_user_lunch.cron_tab.send_statistical_mail_by_week'),
    ('* 10 29 * 5', 'api_user_lunch.cron_tab.send_statistical_mail_by_month'),
    ('* 10 * * *', 'api_event.cron_tab.get_birthday_events'),
    ('* 09 * * 0-4', 'api_event.cron_tab.reminder_admin_set_birthday_slack'),
    ('0 0 15 12 *', 'api_workday.cron_tab.create_remain_leave_for_next_year'),
    ('30 17 31 12 *', 'api_workday.cron_tab.add_annual_leave_last_year_for_next_year'),
    ('* 08 * * *', 'api_workday.services.cron_tab.get_leave_today'),
]

LEAVE_NOTIFICATION_SLACK_API = env('LEAVE_NOTIFICATION_SLACK_API',
                                   default='https://hooks.slack.com/services/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')
LUNCH_NOTIFICATION_SLACK_API = env('LUNCH_NOTIFICATION_SLACK_API',
                                   default='https://hooks.slack.com/services/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')
