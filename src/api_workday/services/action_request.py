from django.db import transaction
from lunarcalendar import Converter, Solar
from api_workday.models.request_off import RequestOff
from api_workday.models.request_detail import RequestDetail
from api_workday.serializers.action_request import RequestDetailSerializer
from api_workday.constants.date import Workday
from api_company.models import Company
from django.utils import timezone
from datetime import datetime
from api_workday.services.send_mail import SendMailRequestOff
from rest_framework.exceptions import APIException
from api_workday.models.date_off import DateOff
from django.db.models import Q
from api_user.models import Profile
from api_user_lunch.models import UserLunch
from api_workday.services.remain_leave import RemainLeaveService
from api_workday.services.date_off import DateOffService
from api_workday.models.remain_leave import RemainLeave


class ActionRequestService:

    @classmethod
    def create_action_user(cls, request_off, profile):
        if request_off.type_off.type == 1:
            profile = Profile.objects.filter(user__is_superuser=True, user__admin=True, user__active=True).first()
        data = {
            "request_off": request_off.id,
            "approve": profile.id
        }
        serializer = RequestDetailSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(request_off_id=request_off.id)

    @classmethod
    def action_approve(cls, request_off_id, user, comment):
        company_setting = Company.objects.all().first()
        month_annual_leave_last_year = company_setting.expired_annual_leave_last_year
        user_action = RequestDetail.objects.filter(request_off_id=request_off_id)
        request_off, request_detail, list_email_manage, list_date_off = cls.get_request_helper(request_off_id, user)
        if request_detail.status or request_off.status == Workday.STATUS_CANCEL:
            return request_detail
        level = request_off.profile.maximum_level_approved
        with transaction.atomic():
            if request_off.status != Workday.STATUS_CANCEL:
                condition = user_action.count() < level and user.line_manager is not None \
                            and request_off.type_off.type != 1
                if condition:
                    request_off.status = Workday.STATUS_FORWARDED
                    request_off.save()
                    cls.create_action_user(request_off, user.line_manager)
                    email = {
                        'user': [request_off.profile.user.email],
                        'admin': [user.line_manager.user.email]
                    }
                    SendMailRequestOff.send_forward_request(type_off=request_off.type_off, name_admin=user.name,
                                                            name_admin_manage=user.line_manager.name,
                                                            name_user=request_off.profile.name,
                                                            email=email,
                                                            date_off=request_off.date_off.all())
                else:
                    request_off.status = Workday.STATUS_APPROVED

                    if request_off.type_off.add_sub_day_off == Workday.ANNUAL_LEAVE:
                        if len(set([date_off.date.year for date_off in list_date_off])) > 1:
                            cls.handle_approve_with_another_year(list_date_off, request_off)
                        elif list_date_off.first().date.year == datetime.now().year - 1:
                            RemainLeaveService.handle_annual_leave_last_year(
                                request_off.profile, DateOffService.get_num_days_off(request_off))
                        elif list_date_off.first().date.year == datetime.now().year:
                            # day off have July and June
                            if len(set([date_off.date.month for date_off in
                                        list_date_off])) > 1 and list_date_off.first().date.month == (
                                    month_annual_leave_last_year or month_annual_leave_last_year - 1):

                                list_date_present_month = list(
                                    filter(lambda date_off: date_off.date.month == month_annual_leave_last_year - 1,
                                           list_date_off))
                                list_date_next_month = list(
                                    filter(lambda date_off: date_off.date.month == month_annual_leave_last_year,
                                           list_date_off))

                                RemainLeaveService.handle_annual_leave(request_off.profile,
                                                                       DateOffService.get_num_days_off_by_list_date(
                                                                           list_date_present_month), True)
                                RemainLeaveService.handle_annual_leave(request_off.profile,
                                                                       DateOffService.get_num_days_off_by_list_date(
                                                                           list_date_next_month))

                            # day off of month in [7, 12]
                            elif list_date_off.first().date.month > month_annual_leave_last_year - 1:
                                RemainLeaveService.handle_annual_leave(request_off.profile,
                                                                       DateOffService.get_num_days_off(
                                                                           request_off))
                            # day off of month in [1, 6]
                            else:
                                RemainLeaveService.handle_annual_leave(request_off.profile,
                                                                       DateOffService.get_num_days_off(
                                                                           request_off), True)
                        else:
                            RemainLeaveService.handle_annual_leave_next_year(
                                request_off.profile, DateOffService.get_num_days_off(request_off))

                    request_off.save()
                    cls.change_lunch(list_date_off, request_off)

                    SendMailRequestOff.send_approve_request_to_user(type_off=request_off.type_off,
                                                                    name_admin=user.name,
                                                                    name_user=request_off.profile.name,
                                                                    list_email=[request_off.profile.user.email],
                                                                    date_off=request_off.date_off.all())

                    SendMailRequestOff.send_approve_request_to_manage(type_off=request_off.type_off,
                                                                      name_user=request_off.profile.name,
                                                                      email_user=request_off.profile.user.email,
                                                                      list_email=list_email_manage,
                                                                      date_off=request_off.date_off.all())
            request_detail.status = Workday.STATUS_APPROVED
            request_detail.comment = comment
            request_detail.save()
        return request_detail

    @classmethod
    def action_reject(cls, request_off_id, user, comment):
        request_off, request_detail, list_email_manage, list_date_off = cls.get_request_helper(request_off_id, user)
        if request_detail.status or request_off.status == Workday.STATUS_CANCEL:
            return request_detail
        with transaction.atomic():
            request_off.status = Workday.STATUS_REJECTED
            request_off.save()
            request_detail.status = Workday.STATUS_REJECTED
            request_detail.comment = comment
            request_detail.save()
            SendMailRequestOff.send_reject_request(type_off=request_off.type_off,
                                                   name_user=request_off.profile.name, name_admin=user.name,
                                                   reason=request_detail.comment,
                                                   list_email=[request_off.profile.user.email],
                                                   list_email_admin=list_email_manage)

        return request_detail

    @classmethod
    def action_cancel(cls, request_off_id, profile):
        if profile.user.is_staff:
            request_off = RequestOff.objects.filter(id=request_off_id).first()
        else:
            request_off = RequestOff.objects.filter(id=request_off_id, profile=profile).first()
            if request_off.status == Workday.STATUS_CANCEL:
                raise APIException('The request was canceled earlier')
        date_offs = request_off.date_off.order_by('date')
        if not cls.allow_or_not_cancel(date_offs.first(), profile):
            raise APIException('Cancellation can only be made 1 hour in advance')
        if request_off.status == Workday.STATUS_APPROVED and DateOffService.get_num_days_off(
                request_off) > 0:
            remain_leave_last_year = RemainLeave.objects.filter(year=datetime.now().year - 1,
                                                                profile_id=request_off.profile.id).first()
            if remain_leave_last_year is not None:
                if len(set([date_off.date.year for date_off in date_offs])) > 1:
                    cls.handle_cancel_request_with_another_year(remain_leave_last_year, request_off)
                elif date_offs.first().date.year == datetime.now().year - 1:
                    RemainLeaveService.handle_annual_leave_last_year(request_off.profile,
                                                                     -DateOffService.get_num_days_off(request_off))
                else:
                    cls.handle_cancel_request(remain_leave_last_year, request_off)
            else:
                RemainLeaveService.handle_annual_leave(request_off.profile,
                                                       -DateOffService.get_num_days_off(request_off))
        request_off.status = Workday.STATUS_CANCEL
        request_off.save()
        request_detail = RequestDetail.objects.filter(request_off_id=request_off_id)
        list_email_admin = [item.approve.user.email for item in request_detail]
        SendMailRequestOff.send_cancel_request(request_off.type_off, profile.name, list_email_admin, date_offs)
        return request_off

    @classmethod
    def allow_or_not_cancel(cls, date_off, profile):
        if profile.user.is_staff:
            return True
        current_date = timezone.now().astimezone().date()
        if date_off.date >= current_date:
            return True
        return False

    @classmethod
    def get_request_canceled(cls, request_off):
        company_setting = Company.objects.all().first()
        if not company_setting:
            return Exception('Company setting not found')
        month_use_annual_leave_last_year = company_setting.expired_annual_leave_last_year

        list_date_approve = [date_off for date_off in
                             DateOff.objects.filter(request_off_id__profile_id=request_off.profile.id,
                                                    request_off_id__status=Workday.STATUS_APPROVED)]

        list_date_by_request_off = [date_off for date_off in
                                    DateOff.objects.filter(request_off_id=request_off.id)]

        list_date_out_sub_month = list(filter(lambda date_off:
                                              date_off.date.month > month_use_annual_leave_last_year - 1,
                                              list_date_by_request_off))
        list_date_in_sub_month = list(
            filter(lambda date_off: date_off.date.month < month_use_annual_leave_last_year,
                   list_date_by_request_off))

        list_date_approve_in_sub_month = list(
            filter(lambda date_off: date_off.date.month < month_use_annual_leave_last_year,
                   list_date_approve))
        list_date_all = list_date_approve_in_sub_month + list_date_in_sub_month

        list_date_approve_in_sub_month_not_request_off = list(
            filter(lambda date_off: list_date_all.count(date_off) == 1, list_date_all))

        num_days_off_in_sub_month_not_request = DateOffService.get_num_days_off_by_list_date(
            list_date_approve_in_sub_month_not_request_off)

        num_days_off_in_sub_month_by_request = DateOffService.get_num_days_off_by_list_date(
            list_date_in_sub_month)
        return num_days_off_in_sub_month_not_request, num_days_off_in_sub_month_by_request, list_date_out_sub_month

    @classmethod
    def count_request(cls, profile):
        request_detail = RequestDetail.objects.filter(approve=profile)
        count = request_detail.filter(Q(status=None) & ~Q(request_off__status=Workday.STATUS_CANCEL)).count()
        return count

    @classmethod
    def get_request_helper(cls, request_off_id, user):
        request_off = RequestOff.objects.filter(id=request_off_id).first()
        request_detail = RequestDetail.objects.filter(request_off_id=request_off_id)
        list_email_admin = [item.approve.user.email for item in request_detail]
        request_detail = request_detail.filter(approve=user).first()
        list_date_off = DateOff.objects.filter(request_off__id=request_off_id)
        return request_off, request_detail, list_email_admin, list_date_off

    @classmethod
    def handle_approve_with_another_year(cls, list_date_off, request_off):
        present_year = datetime.now().year
        list_date_present_year = list(filter(lambda date_off: date_off.date.year == present_year, list_date_off))
        list_date_off_all = list(list_date_off) + list_date_present_year
        list_date_another_year = list(filter(lambda date_off: list_date_off_all.count(date_off) == 1,
                                             list_date_off_all))
        if list_date_another_year[0].date.year == datetime.now().year - 1:
            RemainLeaveService.handle_annual_leave(
                request_off.profile, DateOffService.get_num_days_off_by_list_date(list_date_present_year), True)
            RemainLeaveService.handle_annual_leave_last_year(
                request_off.profile, DateOffService.get_num_days_off_by_list_date(list_date_another_year))
        else:
            RemainLeaveService.handle_annual_leave(
                request_off.profile, DateOffService.get_num_days_off_by_list_date(list_date_present_year))
            RemainLeaveService.handle_annual_leave_next_year(
                request_off.profile, DateOffService.get_num_days_off_by_list_date(list_date_another_year))

    @classmethod
    def handle_cancel_request(cls, remain_leave_last_year, request_off):
        num_days_off_on_sub_month_not_request_off, \
            num_days_off_on_sub_month_by_request_off, \
            list_date_out_sub_month = cls.get_request_canceled(request_off)
        if num_days_off_on_sub_month_not_request_off >= remain_leave_last_year.current_days_off:
            RemainLeaveService.handle_annual_leave(request_off.profile, -num_days_off_on_sub_month_by_request_off)
        else:
            if num_days_off_on_sub_month_not_request_off == 0:
                if num_days_off_on_sub_month_by_request_off - remain_leave_last_year.current_days_off > 0:
                    RemainLeaveService.handle_annual_leave(request_off.profile,
                                                           -remain_leave_last_year.current_days_off,
                                                           True)
                    RemainLeaveService.handle_annual_leave(request_off.profile,
                                                           remain_leave_last_year.current_days_off -
                                                           num_days_off_on_sub_month_by_request_off)
                else:
                    RemainLeaveService.handle_annual_leave(
                        request_off.profile, - num_days_off_on_sub_month_by_request_off, True)

            elif num_days_off_on_sub_month_not_request_off > remain_leave_last_year. \
                    current_days_off:
                RemainLeaveService.handle_annual_leave(request_off.profile, -num_days_off_on_sub_month_by_request_off)
            else:
                if num_days_off_on_sub_month_by_request_off + num_days_off_on_sub_month_not_request_off - \
                        remain_leave_last_year.current_days_off > 0:
                    RemainLeaveService.handle_annual_leave(request_off.profile,
                                                           num_days_off_on_sub_month_not_request_off -
                                                           remain_leave_last_year.current_days_off, True)
                    RemainLeaveService.handle_annual_leave(request_off.profile, remain_leave_last_year.current_days_off
                                                           - num_days_off_on_sub_month_by_request_off -
                                                           num_days_off_on_sub_month_not_request_off)
                else:
                    RemainLeaveService.handle_annual_leave(request_off.profile,
                                                           - num_days_off_on_sub_month_by_request_off, True)
            RemainLeaveService.handle_annual_leave(
                request_off.profile,
                -DateOffService.get_num_days_off_by_list_date(
                    list_date_out_sub_month))

    @classmethod
    def handle_cancel_request_with_another_year(cls, remain_leave_last_year, request_off):
        present_year = datetime.now().year
        list_date = DateOff.objects.filter(request_off_id=request_off.id)
        list_date_present_year = list(filter(lambda date_off: date_off.date.year == present_year, list_date))
        list_date_off_all = list(list_date) + list_date_present_year
        list_date_another_year = list(filter(lambda date_off: list_date_off_all.count(date_off) == 1,
                                             list_date_off_all))

        if list_date_another_year[0].date.year == datetime.now().year - 1:
            RemainLeaveService.handle_annual_leave(request_off.profile,
                                                   -DateOffService.get_num_days_off_by_list_date(
                                                       list_date_present_year), True)

            RemainLeaveService.handle_annual_leave_last_year(
                request_off.profile, -DateOffService.get_num_days_off_by_list_date(list_date_another_year))
        else:
            RemainLeaveService.handle_annual_leave(
                request_off.profile, -DateOffService.get_num_days_off_by_list_date(list_date_present_year))
            RemainLeaveService.handle_annual_leave_next_year(
                request_off.profile, -DateOffService.get_num_days_off_by_list_date(list_date_another_year))

    @classmethod
    def change_lunch(cls, list_date, request_off):
        for date_off in list_date:
            user_lunch = UserLunch.objects.filter(
                profile_id=request_off.profile.id,
                date=date_off.date)
            if date_off.lunch:
                if not user_lunch.exists():
                    data = {
                        'date': date_off.date
                    }
                    solar = Solar(date_off.date.year, date_off.date.month, date_off.date.day)
                    lunar = Converter.Solar2Lunar(solar)
                    if request_off.profile.veggie and (lunar.day == 15 or lunar.day == 1):
                        data['has_veggie'] = True
                    UserLunch.objects.create(
                        date=data.get('date'),
                        has_veggie=data.get('has_veggie', False),
                        profile_id=request_off.profile.id,
                    )
            else:
                if user_lunch.exists():
                    user_lunch.delete()


class FilterActionRequestServices:
    @classmethod
    def filter_multipart(cls, queryset, year, month, day, status, search):
        if year:
            date_off = DateOff.objects.filter(date__year=year)
            if month:
                date_off = date_off.filter(date__month=month)
                if day:
                    date_off = date_off.filter(date__day=day)
            queryset = queryset.filter(request_off__date_off__in=date_off)
        if status:
            queryset = queryset.filter(request_off__status=status)

        if search:
            queryset = queryset.filter(Q(request_off__profile__name__icontains=search) | Q(
                request_off__profile__user__email__icontains=search) | Q(request_off__reason__icontains=search))
        queryset = list(set(queryset))
        queryset.sort(reverse=True, key=sort_helper)
        return queryset


class FilterRequestServices:
    @classmethod
    def filter_multipart(cls, queryset, year, month, day, status, search):
        if year:
            date_off = DateOff.objects.filter(date__year=year)
            if month:
                date_off = date_off.filter(date__month=month)
                if day:
                    date_off = date_off.filter(date__day=day)
            queryset = queryset.filter(date_off__in=date_off)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(Q(profile__name__icontains=search) | Q(
                profile__user__email__icontains=search) | Q(reason__icontains=search))
        queryset = list(set(queryset))
        queryset.sort(reverse=True, key=sort_helper)
        return queryset


def sort_helper(data):
    return data.created_at.timestamp()
