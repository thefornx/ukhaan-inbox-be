from django.db import models


class MessengerLog(models.Model):
    body = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ukhaan_messenger_log'
