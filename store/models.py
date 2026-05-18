from django.db import models

from account.models import Page


class Brand(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='brands',
    )

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    logo_dark_url = models.URLField(blank=True, default='')
    logo_light_url = models.URLField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_brands'


class Branch(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='branches',
    )

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    address_text = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    lat = models.FloatField()
    lon = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_branches'
