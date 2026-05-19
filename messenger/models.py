from django.db import models


class MessengerLog(models.Model):
    body = models.JSONField()
    signature = models.CharField(max_length=255, null=True, blank=True)
    is_valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ukhaan_messenger_log'


class MessengerEvent(models.Model):
    EVENT_TYPES = (
        ('message', 'message'),
        ('postback', 'postback'),
        ('delivery', 'delivery'),
        ('read', 'read'),
        ('reaction', 'reaction'),
        ('optin', 'optin'),
        ('referral', 'referral'),
        ('echo', 'echo'),
        ('unknown', 'unknown'),
    )

    page_facebook_id = models.CharField(max_length=120)
    psid = models.CharField(max_length=120)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES)
    mid = models.CharField(max_length=120, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    payload = models.JSONField()
    is_echo = models.BooleanField(default=False)
    event_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ukhaan_messenger_events'
        indexes = [
            models.Index(fields=['page_facebook_id', 'psid']),
            models.Index(fields=['mid']),
        ]
