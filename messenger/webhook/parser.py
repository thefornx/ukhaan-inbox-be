from datetime import datetime, timezone


def classify(messaging):
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


def parse(page_id, messaging):
    sender = (messaging.get('sender') or {}).get('id', '')
    recipient = (messaging.get('recipient') or {}).get('id', '')
    timestamp = messaging.get('timestamp')

    event_type, mid, text, is_echo = classify(messaging)
    psid = sender if sender and sender != page_id else recipient

    event_at = None
    if isinstance(timestamp, (int, float)):
        event_at = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)

    return {
        'page_facebook_id': page_id,
        'psid': psid,
        'event_type': event_type,
        'mid': mid,
        'text': text,
        'payload': messaging,
        'is_echo': is_echo,
        'event_at': event_at,
    }
