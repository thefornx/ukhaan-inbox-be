import graphene

from account.graphql.mutations.authenticate import AuthenticateMutation
from account.graphql.types import UserType, PageType
from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    page = graphene.Field(PageType, id=graphene.Int())

    @staticmethod
    @login_required
    def resolve_me(_root, info):
        return info.context.user

    @staticmethod
    @login_required
    @business_required
    def resolve_page(_root, info):
        return info.context.business

class Mutation(graphene.ObjectType):
    authenticate = AuthenticateMutation.Field()
