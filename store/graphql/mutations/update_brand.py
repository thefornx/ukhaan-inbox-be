import graphene

from core.graphql.decorators.login_required import login_required
from store.graphql.mutations._helpers import get_owned_or_raise
from store.graphql.types import BrandType
from store.models import Brand


class UpdateBrandInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()
    is_active = graphene.Boolean()
    logo_dark_url = graphene.String()
    logo_light_url = graphene.String()


class UpdateBrandMutation(graphene.Mutation):
    class Arguments:
        input = UpdateBrandInput(required=True)

    brand = graphene.Field(BrandType)

    @classmethod
    @login_required
    def mutate(cls, _root, info, input):
        user = info.context.user
        brand = get_owned_or_raise(Brand, user, input.id)

        for field in ('name', 'description', 'is_active', 'logo_dark_url', 'logo_light_url'):
            value = getattr(input, field, None)
            if value is not None:
                setattr(brand, field, value)
        brand.save()

        return UpdateBrandMutation(brand=brand)
