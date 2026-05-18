import graphene
from graphene_django import DjangoObjectType

from store.models import Brand, Branch


class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = '__all__'
        interfaces = (graphene.relay.Node,)


class BranchType(DjangoObjectType):
    class Meta:
        model = Branch
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
