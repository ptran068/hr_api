from rest_framework import routers
from .views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'photo', PhotoViewSet, basename="photo")
router.register(r'bank', UserBankViewSet, basename="bank")
router.register(r'title', TitleViewSet, basename="title")
router.register(r'bank_list', BankViewSet, basename="bank-list")
router.register(r'contact', UserContactViewSet, basename="contact")
router.register(r'education', UserEducationViewSet, basename="education")
router.register(r'family', UserFamilyMembersViewSet, basename="family")
router.register(r'identity', UserIdentityViewSet, basename="identity")
router.register(r'insurance', UserInsuranceViewSet, basename="insurance")
router.register(r'profile', ProfileViewSet, basename="profile")
router.register(r'', UserViewSet, basename="user")

urlpatterns = router.urls
