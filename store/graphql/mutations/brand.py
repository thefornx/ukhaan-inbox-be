import graphene
from graphql import GraphQLError

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from store.graphql.types import BrandType
from store.models import Brand


class BrandInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    logo_light_url = graphene.String(required=True)
    logo_dark_url = graphene.String(required=True)
    code = graphene.String()


class CreateBrandMutation(graphene.Mutation):
    class Arguments:
        input = BrandInput(required=True)

    brand = graphene.Field(BrandType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, input):
        brand = Brand.objects.create(page=info.context.business, **input)
        return CreateBrandMutation(brand=brand)


class UpdateBrandMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = BrandInput(required=True)

    brand = graphene.Field(BrandType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id, input):
        try:
            brand = Brand.objects.get(pk=id, page=info.context.business)
        except Brand.DoesNotExist:
            raise GraphQLError('Brand not found')

        for key, value in input.items():
            setattr(brand, key, value)
        brand.save()

        return UpdateBrandMutation(brand=brand)


class DeleteBrandMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id):
        deleted, _ = Brand.objects.filter(pk=id, page=info.context.business).delete()
        return DeleteBrandMutation(ok=deleted > 0)
