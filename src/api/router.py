from django.conf.urls import include, url
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import include

from api_admin.views import AdminViewSet
from api_base.views import ActionViewSet, LoginViewSet
from api_workday.views import DateViewSet, LunchViewSet
from api_workday.views.propose_leave import ProposeLeaveViewSet

router = DefaultRouter()

# Define url in here
router.register(r'actions', ActionViewSet, basename="actions")
router.register(r'admin', AdminViewSet, basename="admin")
router.register(r'date', DateViewSet, basename="date")
router.register(r'login', LoginViewSet, basename="login")
router.register(r'lunch', LunchViewSet, basename="lunch")
router.register(r'leave', ProposeLeaveViewSet, basename="leave")

urlpatterns = [
    url(r'^', include(router.urls)),
]
