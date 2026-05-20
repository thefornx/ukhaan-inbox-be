from decimal import Decimal

from django.db import transaction

from order.models import Order, OrderItem


def get_or_create_cart(page, psid):
    cart, _ = Order.objects.get_or_create(
        page=page, psid=psid, status='cart',
        defaults={'total': 0},
    )
    return cart


def get_open_cart(page, psid):
    return (
        Order.objects.filter(page=page, psid=psid, status='cart')
        .prefetch_related('items__product', 'items__variant__images')
        .first()
    )


def clear_cart(page, psid):
    deleted, _ = Order.objects.filter(page=page, psid=psid, status='cart').delete()
    return deleted > 0


@transaction.atomic
def add_to_cart(page, psid, product, quantity=1):
    cart = get_or_create_cart(page, psid)
    variant = product.variants.first()
    unit_price = variant.price if variant else Decimal('0')

    item, created = OrderItem.objects.get_or_create(
        order=cart, product=product, variant=variant,
        defaults={'quantity': quantity, 'unit_price': unit_price},
    )
    if not created:
        item.quantity += quantity
        item.save()

    cart.total = sum(
        (i.quantity * i.unit_price for i in cart.items.all()),
        Decimal('0'),
    )
    cart.save()
    return cart
