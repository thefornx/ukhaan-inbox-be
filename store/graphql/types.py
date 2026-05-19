import graphene
from graphene_django import DjangoObjectType

from store.models import Brand, Branch, OpeningHours


class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = '__all__'


class OpeningHoursType(DjangoObjectType):
    class Meta:
        model = OpeningHours
        fields = '__all__'


class BranchType(DjangoObjectType):
    opening_hours = graphene.List(OpeningHoursType)

    class Meta:
        model = Branch
        fields = '__all__'

    @staticmethod
    def resolve_opening_hours(parent, info):
        return parent.opening_hours.all()
