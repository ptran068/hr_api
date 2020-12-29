from django.urls import path
from . import views

urlpatterns = [
    path('slack-event', views.SlackEvents.as_view(), name='events'),
    path('', views.EventsList.as_view(), name='events'),
    path('users', views.EventUsersList.as_view(), name='event-users'),
    path('<uuid:pk>', views.EventsList.as_view()),
]
