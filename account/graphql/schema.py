import graphene

from account.graphql.mutations.authenticate import AuthenticateMutation
from account.graphql.types import UserType, PageType
from core.graphql.decorators.login_required import login_required
from .resolvers import resolve_page

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    page = graphene.Field(PageType, id=graphene.Int())

    @staticmethod
    @login_required
    def resolve_me(_root, info):
        return info.context.user

    @staticmethod
    @login_required
    def resolve_page(root, id, info):
        return resolve_page(root, info, id)

class Mutation(graphene.ObjectType):
    authenticate = AuthenticateMutation.Field()
