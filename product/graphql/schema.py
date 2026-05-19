import graphene

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from product.graphql.mutations.category import (
    CreateCategoryMutation,
    UpdateCategoryMutation,
    DeleteCategoryMutation,
)
from product.graphql.mutations.product import (
    CreateProductMutation,
    UpdateProductMutation,
    DeleteProductMutation,
)
from product.graphql.mutations.variant import (
    CreateProductVariantMutation,
    UpdateProductVariantMutation,
    DeleteProductVariantMutation,
)
from product.graphql.resolvers import (
    resolve_categories,
    resolve_category,
    resolve_products,
    resolve_product,
    resolve_variants,
    resolve_variant,
)
from product.graphql.types import CategoryType, ProductType, ProductVariantType


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))

    products = graphene.List(
        ProductType,
        name=graphene.String(),
        category_id=graphene.Int(),
        brand_id=graphene.Int(),
        price_min=graphene.Decimal(),
        price_max=graphene.Decimal(),
    )
    product = graphene.Field(ProductType, id=graphene.Int(required=True))

    product_variants = graphene.List(ProductVariantType, product_id=graphene.Int())
    product_variant = graphene.Field(ProductVariantType, id=graphene.Int(required=True))

    @staticmethod
    @login_required
    @business_required
    def resolve_categories(_root, info):
        return resolve_categories(info.context.business)

    @staticmethod
    @login_required
    @business_required
    def resolve_category(_root, info, id):
        return resolve_category(info.context.business, id)

    @staticmethod
    @login_required
    @business_required
    def resolve_products(_root, info, name=None, category_id=None, brand_id=None, price_min=None, price_max=None):
        return resolve_products(
            info.context.business,
            name=name,
            category_id=category_id,
            brand_id=brand_id,
            price_min=price_min,
            price_max=price_max,
        )

    @staticmethod
    @login_required
    @business_required
    def resolve_product(_root, info, id):
        return resolve_product(info.context.business, id)

    @staticmethod
    @login_required
    @business_required
    def resolve_product_variants(_root, info, product_id=None):
        return resolve_variants(info.context.business, product_id=product_id)

    @staticmethod
    @login_required
    @business_required
    def resolve_product_variant(_root, info, id):
        return resolve_variant(info.context.business, id)


class Mutation(graphene.ObjectType):
    create_category = CreateCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()

    create_product = CreateProductMutation.Field()
    update_product = UpdateProductMutation.Field()
    delete_product = DeleteProductMutation.Field()

    create_product_variant = CreateProductVariantMutation.Field()
    update_product_variant = UpdateProductVariantMutation.Field()
    delete_product_variant = DeleteProductVariantMutation.Field()
