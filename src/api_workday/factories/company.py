
import factory
from api_company.models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company
