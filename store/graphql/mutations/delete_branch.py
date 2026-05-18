import graphene

from core.graphql.decorators.login_required import login_required
from store.graphql.mutations._helpers import get_owned_or_raise
from store.models import Branch


class DeleteBranchInput(graphene.InputObjectType):
    id = graphene.ID(required=True)


class DeleteBranchMutation(graphene.Mutation):
    class Arguments:
        input = DeleteBranchInput(required=True)

    ok = graphene.Boolean()

    @classmethod
    @login_required
    def mutate(cls, _root, info, input):
        user = info.context.user
        branch = get_owned_or_raise(Branch, user, input.id)
        branch.delete()
        return DeleteBranchMutation(ok=True)
