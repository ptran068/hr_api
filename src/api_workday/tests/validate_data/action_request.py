from faker import Factory
from api_workday.factories.type_off import TypeOffFactory
from api_workday.constants.date import Workday

faker = Factory.create()


class ActionRequest:
    @classmethod
    def approve(cls, request_id):
        return {
            'request_off_id': request_id,
            'action': Workday.STATUS_APPROVED
        }

    @classmethod
    def reject(cls, request_id):
        return {
            'request_off_id': request_id,
            'action': Workday.STATUS_REJECTED,
            'comment': ''
        }

    @classmethod
    def cancel(cls, request_id):
        return {
            'request_off_id': request_id,
            'action': Workday.STATUS_CANCEL
        }
