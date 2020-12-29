from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    join(BASE_DIR, "static"),
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default='Management Admin <management-admin@paradox.ai>')
DEFAULT_EMAIL_ADMIN = env("DEFAULT_EMAIL_ADMIN", default='admin@paradox.ai')
