from rest_framework import routers
from .views import TeamViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', TeamViewSet, basename="team")

urlpatterns = router.urls
