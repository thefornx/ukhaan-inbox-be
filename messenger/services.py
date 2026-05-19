import hashlib
import hmac
from datetime import datetime, timezone

from django.conf import settings

from messenger.models import MessengerEvent


class MessengerWebhook:
    signature_prefix = 'sha256='

    def __init__(self):
        self.app_secret = settings.FACEBOOK.get('APP_SECRET') or ''
        self.verify_token = settings.MESSENGER.get('VERIFY_TOKEN') or ''

    def verify_subscription(self, mode, token, challenge):
        if mode == 'subscribe' and token and token == self.verify_token:
            return challenge
        return None

    def verify_signature(self, raw_body, header):
        if not self.app_secret or not header:
            return False
        if not header.startswith(self.signature_prefix):
            return False
        expected = hmac.new(
            self.app_secret.encode('utf-8'),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, header[len(self.signature_prefix):])

    def process(self, body):
        if body.get('object') != 'page':
            return
        for entry in body.get('entry', []) or []:
            page_id = str(entry.get('id', ''))
            for messaging in entry.get('messaging', []) or []:
                self._handle_event(page_id, messaging)

    def _handle_event(self, page_id, messaging):
        sender = (messaging.get('sender') or {}).get('id', '')
        recipient = (messaging.get('recipient') or {}).get('id', '')
        timestamp = messaging.get('timestamp')

        event_type, mid, text, is_echo = self._classify(messaging)
        psid = sender if sender and sender != page_id else recipient

        event_at = None
        if isinstance(timestamp, (int, float)):
            event_at = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)

        MessengerEvent.objects.create(
            page_facebook_id=page_id,
            psid=psid,
            event_type=event_type,
            mid=mid,
            text=text,
            payload=messaging,
            is_echo=is_echo,
            event_at=event_at,
        )

        self._dispatch_assistant(page_id, psid, event_type, text, messaging)

    def _dispatch_assistant(self, page_id, psid, event_type, text, messaging):
        from account.models import Page
        from core.services.assistant import Assistant

        if event_type == 'message' and text:
            page = Page.objects.filter(facebook_id=page_id).first()
            if page:
                try:
                    Assistant(page).respond(psid, text)
                except Exception as exc:
                    print(f'[assistant] respond failed: {exc}')
        elif event_type == 'postback':
            payload = (messaging.get('postback') or {}).get('payload', '')
            if not payload:
                return
            page = Page.objects.filter(facebook_id=page_id).first()
            if page:
                try:
                    Assistant(page).handle_postback(psid, payload)
                except Exception as exc:
                    print(f'[assistant] postback failed: {exc}')

    def _classify(self, messaging):
        if 'message' in messaging:
            msg = messaging['message'] or {}
            is_echo = bool(msg.get('is_echo'))
            return (
                'echo' if is_echo else 'message',
                msg.get('mid'),
                msg.get('text'),
                is_echo,
            )
        if 'postback' in messaging:
            pb = messaging['postback'] or {}
            return 'postback', pb.get('mid'), pb.get('title'), False
        if 'delivery' in messaging:
            return 'delivery', None, None, False
        if 'read' in messaging:
            return 'read', None, None, False
        if 'reaction' in messaging:
            return 'reaction', None, None, False
        if 'optin' in messaging:
            return 'optin', None, None, False
        if 'referral' in messaging:
            return 'referral', None, None, False
        return 'unknown', None, None, False
