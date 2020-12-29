from django.urls import path
from . import views

urlpatterns = [
    path('list', views.LunchesList.as_view(), name='lunches'),
    path('create', views.HandleLunch.as_view(), name='create-lunch'),
    path('action/<uuid:pk>', views.HandleLunch.as_view(), name='modify-lunch')
]
