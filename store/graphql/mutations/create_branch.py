import graphene

from core.graphql.decorators.login_required import login_required
from store.graphql.mutations._helpers import get_user_page
from store.graphql.types import BranchType
from store.models import Branch


class CreateBranchInput(graphene.InputObjectType):
    page_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    address_text = graphene.String()
    is_active = graphene.Boolean()
    lat = graphene.Float(required=True)
    lon = graphene.Float(required=True)


class CreateBranchMutation(graphene.Mutation):
    class Arguments:
        input = CreateBranchInput(required=True)

    branch = graphene.Field(BranchType)

    @classmethod
    @login_required
    def mutate(cls, _root, info, input):
        user = info.context.user
        page = get_user_page(user, input.page_id)

        branch = Branch.objects.create(
            page=page,
            name=input.name,
            description=input.description or '',
            address_text=input.address_text or '',
            is_active=input.is_active if input.is_active is not None else True,
            lat=input.lat,
            lon=input.lon,
        )
        return CreateBranchMutation(branch=branch)
