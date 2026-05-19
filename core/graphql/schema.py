import graphene

from account.graphql.schema import Query as AccountQuery
from account.graphql.schema import Mutation as AccountMutation
from store.graphql.schema import Query as StoreQuery
from store.graphql.schema import Mutation as StoreMutation

class Query(
    AccountQuery,
    StoreQuery,
    graphene.ObjectType
):
    pass

class Mutation(
    AccountMutation,
    StoreMutation,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)
