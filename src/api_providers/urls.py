
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HandleProvider.as_view(), name='get-providers'),
    path('create', views.HandleProvider.as_view(), name='create-provider'),
    path('action/<uuid:pk>', views.HandleProvider.as_view(), name='modify-provider')
]