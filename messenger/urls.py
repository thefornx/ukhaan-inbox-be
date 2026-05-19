from django.urls import path

from messenger.views import webhook

urlpatterns = [
    path('messenger', webhook),
]
