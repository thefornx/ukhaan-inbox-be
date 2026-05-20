from decimal import Decimal

import graphene
from django.db import transaction
from graphql import GraphQLError

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from order.graphql.types import OrderType
from order.models import Order, OrderItem
from product.models import Product, ProductVariant


class OrderItemInput(graphene.InputObjectType):
    product_id = graphene.Int(required=True)
    variant_id = graphene.Int()
    quantity = graphene.Int(default_value=1)


class OrderInput(graphene.InputObjectType):
    psid = graphene.String()
    status = graphene.String()
    items = graphene.List(OrderItemInput)


def _get_product(business, product_id):
    try:
        return Product.objects.get(pk=product_id, page=business)
    except Product.DoesNotExist:
        raise GraphQLError('Product not found')


def _get_variant(product, variant_id):
    if variant_id is None:
        return None
    try:
        return ProductVariant.objects.get(pk=variant_id, product=product)
    except ProductVariant.DoesNotExist:
        raise GraphQLError('Variant not found')


def _build_item(business, item_input):
    product = _get_product(business, item_input['product_id'])
    variant = _get_variant(product, item_input.get('variant_id'))
    if variant is not None:
        unit_price = variant.price
    else:
        first = product.variants.first()
        unit_price = first.price if first else Decimal('0')
    return OrderItem(
        product=product,
        variant=variant,
        quantity=item_input.get('quantity', 1),
        unit_price=unit_price,
    )


class CreateOrderMutation(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, input):
        business = info.context.business
        items_data = input.get('items') or []

        with transaction.atomic():
            order = Order.objects.create(
                page=business,
                psid=input.get('psid'),
                status=input.get('status') or 'cart',
                total=0,
            )
            total = Decimal('0')
            for item_input in items_data:
                item = _build_item(business, dict(item_input))
                item.order = order
                item.save()
                total += item.quantity * item.unit_price
            order.total = total
            order.save()

        return CreateOrderMutation(order=order)


class UpdateOrderMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        status = graphene.String()

    order = graphene.Field(OrderType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id, status=None):
        try:
            order = Order.objects.get(pk=id, page=info.context.business)
        except Order.DoesNotExist:
            raise GraphQLError('Order not found')

        if status is not None:
            order.status = status
        order.save()

        return UpdateOrderMutation(order=order)


class DeleteOrderMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id):
        deleted, _ = Order.objects.filter(pk=id, page=info.context.business).delete()
        return DeleteOrderMutation(ok=deleted > 0)
