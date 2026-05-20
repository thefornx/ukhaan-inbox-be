from django.conf import settings

from messenger.handlers import dispatch
from messenger.models import MessengerEvent
from messenger.webhook import parser, signature, subscription


class Webhook:
    def __init__(self):
        self.app_secret = settings.FACEBOOK.get('APP_SECRET') or ''
        self.verify_token = settings.MESSENGER.get('VERIFY_TOKEN') or ''

    def verify_subscription(self, mode, token, challenge):
        return subscription.verify(mode, token, challenge, self.verify_token)

    def verify_signature(self, raw_body, header):
        return signature.verify(raw_body, header, self.app_secret)

    def process(self, body):
        if body.get('object') != 'page':
            return
        for entry in body.get('entry') or []:
            page_id = str(entry.get('id', ''))
            for messaging in entry.get('messaging') or []:
                self._handle(page_id, messaging)

    def _handle(self, page_id, messaging):
        event = MessengerEvent.objects.create(**parser.parse(page_id, messaging))
        dispatch(event, messaging)
