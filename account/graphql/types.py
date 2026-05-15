import graphene
from graphene_django import DjangoConnectionField, DjangoObjectType

from account.models import Page, User

from account.graphql.resolvers import resolve_pages


class PageType(DjangoObjectType):
    class Meta:
        model = Page
        exclude = ('access_token',)
        interfaces = (graphene.relay.Node,)


class UserType(DjangoObjectType):
    pages = DjangoConnectionField(PageType)

    class Meta:
        model = User
        fields = '__all__'

    @staticmethod
    def resolve_pages(parent, info, **kwargs):
        return resolve_pages(parent, info, **kwargs)

