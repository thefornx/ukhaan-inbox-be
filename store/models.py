from django.db import models

from account.models import Page


class Brand(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='brands')
    name = models.CharField(max_length=120)
    logo_light_url = models.TextField()
    logo_dark_url = models.TextField()
    code = models.CharField(max_length=64, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_brands'


class Branch(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=120)
    address_text = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    website = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_branches'


class OpeningHours(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='opening_hours')
    day_of_week = models.IntegerField()
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        db_table = 'ukhaan_opening_hours'
