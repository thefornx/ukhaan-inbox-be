import graphene

from account.graphql.schema import Query as AccountQuery
from account.graphql.schema import Mutation as AccountMutation

class Query(
    AccountQuery,
    graphene.ObjectType
):
    pass

class Mutation(
    AccountMutation,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)
