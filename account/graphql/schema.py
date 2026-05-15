import graphene

from account.graphql.mutations.authenticate import AuthenticateMutation
from account.graphql.types import UserType
from core.graphql.decorators.login_required import login_required

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    @staticmethod
    @login_required
    def resolve_me(_root, info):
        return info.context.user

class Mutation(graphene.ObjectType):
    authenticate = AuthenticateMutation.Field()
