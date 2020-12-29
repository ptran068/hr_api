from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

urlpatterns = [
    url(r'^api/v1/', include(('api.router', 'api'), namespace='v1')),
    url(r'^api/v1/workday/', include('api_workday.urls')),
    url(r'^api/v1/user/', include('api_user.urls')),
    url(r'^api/v1/provider/', include('api_providers.urls')),
    url(r'^api/v1/lunch/', include('api_lunch.urls')),
    url(r'^api/v1/user-lunch/', include('api_user_lunch.urls')),
    url(r'^api/v1/event/', include('api_event.urls')),
    url(r'^api/v1/team/', include('api_team.urls')),
    url(r'^api/v1/company/', include('api_company.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
