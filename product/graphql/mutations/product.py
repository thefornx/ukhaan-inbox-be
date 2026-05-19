import graphene
from graphql import GraphQLError

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from product.graphql.types import ProductType
from product.models import Category, Product
from store.models import Brand


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    sku = graphene.String(required=True)
    category_id = graphene.Int()
    brand_id = graphene.Int()


def _get_category(business, category_id):
    if category_id is None:
        return None
    try:
        return Category.objects.get(pk=category_id, page=business)
    except Category.DoesNotExist:
        raise GraphQLError('Category not found')


def _get_brand(business, brand_id):
    if brand_id is None:
        return None
    try:
        return Brand.objects.get(pk=brand_id, page=business)
    except Brand.DoesNotExist:
        raise GraphQLError('Brand not found')


def _apply_relations(business, product, data):
    if 'category_id' in data:
        product.category = _get_category(business, data.pop('category_id'))
    if 'brand_id' in data:
        product.brand = _get_brand(business, data.pop('brand_id'))


class CreateProductMutation(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, input):
        business = info.context.business
        data = dict(input)
        category = _get_category(business, data.pop('category_id', None))
        brand = _get_brand(business, data.pop('brand_id', None))
        product = Product.objects.create(
            page=business, category=category, brand=brand, **data
        )
        return CreateProductMutation(product=product)


class UpdateProductMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id, input):
        business = info.context.business
        try:
            product = Product.objects.get(pk=id, page=business)
        except Product.DoesNotExist:
            raise GraphQLError('Product not found')

        data = dict(input)
        _apply_relations(business, product, data)
        for key, value in data.items():
            setattr(product, key, value)
        product.save()

        return UpdateProductMutation(product=product)


class DeleteProductMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id):
        deleted, _ = Product.objects.filter(pk=id, page=info.context.business).delete()
        return DeleteProductMutation(ok=deleted > 0)
