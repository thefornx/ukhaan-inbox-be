from django.db import models

from account.models import Page
from product.models import Product, ProductVariant


class Order(models.Model):
    STATUSES = (
        ('cart', 'cart'),
        ('confirmed', 'confirmed'),
        ('paid', 'paid'),
        ('cancelled', 'cancelled'),
    )

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='orders')
    psid = models.CharField(max_length=120, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='cart')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_orders'
        indexes = [models.Index(fields=['page', 'psid', 'status'])]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant, null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'ukhaan_order_items'
