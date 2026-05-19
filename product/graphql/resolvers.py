from graphql import GraphQLError

from product.models import Category, Product, ProductVariant


def resolve_categories(business):
    return Category.objects.filter(page=business)


def resolve_category(business, id):
    try:
        return Category.objects.get(pk=id, page=business)
    except Category.DoesNotExist:
        raise GraphQLError('Category not found')


def resolve_products(business):
    return Product.objects.filter(page=business)


def resolve_product(business, id):
    try:
        return Product.objects.get(pk=id, page=business)
    except Product.DoesNotExist:
        raise GraphQLError('Product not found')


def resolve_variants(business, product_id=None):
    qs = ProductVariant.objects.filter(product__page=business)
    if product_id is not None:
        qs = qs.filter(product_id=product_id)
    return qs


def resolve_variant(business, id):
    try:
        return ProductVariant.objects.get(pk=id, product__page=business)
    except ProductVariant.DoesNotExist:
        raise GraphQLError('Variant not found')
