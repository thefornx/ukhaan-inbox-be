import graphene

from core.graphql.decorators.login_required import login_required
from store.graphql.mutations._helpers import get_owned_or_raise
from store.models import Brand


class DeleteBrandInput(graphene.InputObjectType):
    id = graphene.ID(required=True)


class DeleteBrandMutation(graphene.Mutation):
    class Arguments:
        input = DeleteBrandInput(required=True)

    ok = graphene.Boolean()

    @classmethod
    @login_required
    def mutate(cls, _root, info, input):
        user = info.context.user
        brand = get_owned_or_raise(Brand, user, input.id)
        brand.delete()
        return DeleteBrandMutation(ok=True)
