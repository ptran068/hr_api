from django.urls import path

from api_company.views import CompanyViewSet

company = CompanyViewSet.as_view({
    'post': 'create',
    'patch': 'update',
    'get': 'retrieve'
})

urlpatterns = [
    path('create', company, name='create-company'),
    path('edit', company, name='modify-company'),
    path('', company, name='company')
]
