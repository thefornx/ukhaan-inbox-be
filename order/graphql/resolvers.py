from graphql import GraphQLError

from order.models import Order


def resolve_orders(business, status=None):
    qs = (
        Order.objects.filter(page=business)
        .prefetch_related('items__product', 'items__variant')
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def resolve_order(business, id):
    try:
        return (
            Order.objects.prefetch_related('items__product', 'items__variant')
            .get(pk=id, page=business)
        )
    except Order.DoesNotExist:
        raise GraphQLError('Order not found')
