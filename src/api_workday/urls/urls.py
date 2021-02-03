from django.urls import path

from api_workday.views.action_request import ActionRequest, GetRequestDetail, CountRequestHaveNotBeenApprove
from api_workday.views.admin_statistic import StatisticAdminView
from api_workday.views.user_statistic import StatisticUserView
from api_workday.views.bonus import AddBonusView
from api_workday.views.calendar import CalendarViewSet
from api_workday.views.date_off import DateOffView
from api_workday.views.remain_leave import RemainLeaveViewSet
from api_workday.views.request_off import RequestOffDetail, GetMyRequest, GetAllRequest
from api_workday.views.type_off import TypeOffView, CreateTypeOffView, TypeOffForAdminView
from api_workday.views.holiday import HolidayViewSet

urlpatterns = [
    path('admin/types', TypeOffForAdminView.as_view(), name='type'),
    path('admin/type/create', CreateTypeOffView.as_view(), name='create-type'),
    path('admin/type/edit/<uuid:pk>', TypeOffForAdminView.as_view(), name='modify-type'),
    path('type', TypeOffView.as_view(), name='type'),

    path('request/<uuid:pk>', RequestOffDetail.as_view(), name='request-detail'),
    path('request/create', RequestOffDetail.as_view(), name='create-request'),

    path('date', DateOffView.as_view()),

    path('add_bonus', AddBonusView.as_view(), name='add_bonus'),
    path('remain_leave', RemainLeaveViewSet.as_view({'get': 'list', 'post': 'create'}), name='create_remain_leave'),
    path('retrieve_date', RemainLeaveViewSet.as_view({'get': 'retrieve'}), name='retrieve_date_statistic'),

    path('action', ActionRequest.as_view(), name='action'),
    path('request/management', GetRequestDetail.as_view(), name='management-request'),
    path('request/user', GetMyRequest.as_view(), name='request-user'),

    path('calendar/user', CalendarViewSet.as_view({'get': 'retrieve'}), name='calendar_user'),
    path('calendar/admin', CalendarViewSet.as_view({'get': 'list'}), name='calendar_admin'),

    path('admin', StatisticAdminView.as_view(), name='admin'),
    path('user', StatisticUserView.as_view(), name='user'),

    path('holiday/create', HolidayViewSet.as_view({'post': 'create'}, name='create-holiday')),
    path('holidays', HolidayViewSet.as_view({'get': 'list'}, name='list-holiday')),
    path('holiday/<uuid:pk>', HolidayViewSet.as_view({'delete': 'destroy'}, name='remove-holiday')),
    path('request/management/count', CountRequestHaveNotBeenApprove.as_view(), name='count-request'),
    path('request/admin', GetAllRequest.as_view(), name='request-admin'),
]
