from django.db import models

# Create your models here.

class User(models.Model):
    facebook_id = models.CharField(max_length=120)
    name = models.CharField(max_length=120)
    picture_url = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_users'

class Page(models.Model):
    facebook_id = models.CharField(max_length=120)
    access_token = models.TextField()
    name = models.CharField(max_length=120)
    picture_url = models.TextField()

    users = models.ManyToManyField(
        User,
        through='UserPages',
        related_name='pages',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ukhaan_pages'

class UserPages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ukhaan_user_pages'