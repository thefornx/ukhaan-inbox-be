import graphene

from account.graphql.schema import Query as AccountQuery
from account.graphql.schema import Mutation as AccountMutation
from store.graphql.schema import Query as StoreQuery
from store.graphql.schema import Mutation as StoreMutation
from product.graphql.schema import Query as ProductQuery
from product.graphql.schema import Mutation as ProductMutation

class Query(
    AccountQuery,
    StoreQuery,
    ProductQuery,
    graphene.ObjectType
):
    pass

class Mutation(
    AccountMutation,
    StoreMutation,
    ProductMutation,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)
