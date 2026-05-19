import graphene
from django.db import transaction
from graphql import GraphQLError

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from product.graphql.types import ProductVariantType
from product.models import Product, ProductImage, ProductVariant
from store.models import Branch


class ProductVariantInput(graphene.InputObjectType):
    branch_id = graphene.Int()
    stock = graphene.Int(default_value=0)
    price = graphene.Decimal()
    images = graphene.List(graphene.String)


def _get_branch(business, branch_id):
    if branch_id is None:
        return None
    try:
        return Branch.objects.get(pk=branch_id, page=business)
    except Branch.DoesNotExist:
        raise GraphQLError('Branch not found')


def _sync_images(variant, urls):
    variant.images.all().delete()
    ProductImage.objects.bulk_create([
        ProductImage(variant=variant, url=url) for url in urls
    ])


class CreateProductVariantMutation(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)
        input = ProductVariantInput(required=True)

    variant = graphene.Field(ProductVariantType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, product_id, input):
        business = info.context.business
        try:
            product = Product.objects.get(pk=product_id, page=business)
        except Product.DoesNotExist:
            raise GraphQLError('Product not found')

        data = dict(input)
        images = data.pop('images', None) or []
        branch = _get_branch(business, data.pop('branch_id', None))

        with transaction.atomic():
            variant = ProductVariant.objects.create(
                product=product, branch=branch, **data
            )
            if images:
                _sync_images(variant, images)
        return CreateProductVariantMutation(variant=variant)


class UpdateProductVariantMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProductVariantInput(required=True)

    variant = graphene.Field(ProductVariantType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id, input):
        business = info.context.business
        try:
            variant = ProductVariant.objects.get(pk=id, product__page=business)
        except ProductVariant.DoesNotExist:
            raise GraphQLError('Variant not found')

        data = dict(input)
        images = data.pop('images', None)
        if 'branch_id' in data:
            variant.branch = _get_branch(business, data.pop('branch_id'))

        with transaction.atomic():
            for key, value in data.items():
                setattr(variant, key, value)
            variant.save()
            if images is not None:
                _sync_images(variant, images)

        return UpdateProductVariantMutation(variant=variant)


class DeleteProductVariantMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id):
        deleted, _ = ProductVariant.objects.filter(
            pk=id, product__page=info.context.business
        ).delete()
        return DeleteProductVariantMutation(ok=deleted > 0)
