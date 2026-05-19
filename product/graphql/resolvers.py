from graphql import GraphQLError

from product.models import Category, Product, ProductVariant


def resolve_categories(business):
    return Category.objects.filter(page=business)


def resolve_category(business, id):
    try:
        return Category.objects.get(pk=id, page=business)
    except Category.DoesNotExist:
        raise GraphQLError('Category not found')


def resolve_products(business, name=None, category_id=None, brand_id=None, price_min=None, price_max=None):
    qs = (
        Product.objects.filter(page=business)
        .select_related('brand', 'category')
        .prefetch_related('variants__images')
    )
    if name:
        qs = qs.filter(name__icontains=name)
    if category_id is not None:
        qs = qs.filter(category_id=category_id)
    if brand_id is not None:
        qs = qs.filter(brand_id=brand_id)
    if price_min is not None:
        qs = qs.filter(variants__price__gte=price_min)
    if price_max is not None:
        qs = qs.filter(variants__price__lte=price_max)
    if price_min is not None or price_max is not None:
        qs = qs.distinct()
    return qs


def resolve_product(business, id):
    try:
        return (
            Product.objects.select_related('brand', 'category')
            .prefetch_related('variants__images')
            .get(pk=id, page=business)
        )
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
