import graphene

from core.graphql.decorators.login_required import login_required
from store.graphql.mutations._helpers import get_owned_or_raise
from store.graphql.types import BranchType
from store.models import Branch


class UpdateBranchInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()
    address_text = graphene.String()
    is_active = graphene.Boolean()
    lat = graphene.Float()
    lon = graphene.Float()


class UpdateBranchMutation(graphene.Mutation):
    class Arguments:
        input = UpdateBranchInput(required=True)

    branch = graphene.Field(BranchType)

    @classmethod
    @login_required
    def mutate(cls, _root, info, input):
        user = info.context.user
        branch = get_owned_or_raise(Branch, user, input.id)

        for field in ('name', 'description', 'address_text', 'is_active', 'lat', 'lon'):
            value = getattr(input, field, None)
            if value is not None:
                setattr(branch, field, value)
        branch.save()

        return UpdateBranchMutation(branch=branch)
