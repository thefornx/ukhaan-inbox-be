import graphene

from core.graphql.decorators.login_required import login_required
from store.graphql.mutations._helpers import get_user_page
from store.graphql.types import BrandType
from store.models import Brand


class CreateBrandInput(graphene.InputObjectType):
    page_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    is_active = graphene.Boolean()
    logo_dark_url = graphene.String()
    logo_light_url = graphene.String()


class CreateBrandMutation(graphene.Mutation):
    class Arguments:
        input = CreateBrandInput(required=True)

    brand = graphene.Field(BrandType)

    @classmethod
    @login_required
    def mutate(cls, _root, info, input):
        user = info.context.user
        page = get_user_page(user, input.page_id)

        brand = Brand.objects.create(
            page=page,
            name=input.name,
            description=input.description or '',
            is_active=input.is_active if input.is_active is not None else True,
            logo_dark_url=input.logo_dark_url or '',
            logo_light_url=input.logo_light_url or '',
        )
        return CreateBrandMutation(brand=brand)
