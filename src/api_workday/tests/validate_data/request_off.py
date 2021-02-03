from faker import Factory, Faker
from api_workday.factories.type_off import TypeOffFactory
from datetime import datetime, timedelta

faker = Factory.create()

class Request:

    @classmethod
    def data(self, id):
        date_end = datetime.now().date() + timedelta(1000)
        return {
            "reason": faker.word(),
            "type_id": id,
            "date": [{"date": faker.date_between_dates(date_start=datetime.now().date(), date_end=date_end), "type": "All day", "lunch": "False"}]
        }

    @classmethod
    def data_too_time(cls, id):
        return {
            "reason": faker.word(),
            "type_id": id,
            "date": [{"date": datetime.now().date() - timedelta(5), "type": "All day", "lunch": "False"}]
        }
