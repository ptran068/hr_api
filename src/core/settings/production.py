from .base import *

# For security and performance reasons, DEBUG is turned off
DEBUG = False

CUSTOM_DOMAIN = env('CUSTOM_DOMAIN')
STATIC_URL = 'http://{0}/{1}/'.format(CUSTOM_DOMAIN, 'static')
#
# # Media S3 config
MEDIA_URL = 'http://{0}/{1}/'.format(CUSTOM_DOMAIN, 'media')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    join(BASE_DIR, "static"),
]
EMAIL_BACKEND = 'bandit.backends.smtp.HijackSMTPBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default='Management Admin <management-admin@paradox.ai>')
DEFAULT_EMAIL_ADMIN = env("DEFAULT_EMAIL_ADMIN", default='admin@paradox.ai')