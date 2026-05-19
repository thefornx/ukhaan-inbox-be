from django.db import models

from account.models import Page
from store.models import Brand, Branch


class Category(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='categories')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children',
    )
    name = models.CharField(max_length=120)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_categories'


class Product(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=120)
    category = models.ForeignKey(
        Category, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='products',
    )
    brand = models.ForeignKey(
        Brand, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='products',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_products'


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    branch = models.ForeignKey(
        Branch, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='variants',
    )
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_product_variants'


class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    url = models.TextField()

    class Meta:
        db_table = 'ukhaan_product_images'
