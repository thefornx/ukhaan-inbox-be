import hashlib
import hmac


PREFIX = 'sha256='


def verify(raw_body, header, app_secret):
    if not app_secret or not header or not header.startswith(PREFIX):
        return False
    expected = hmac.new(
        app_secret.encode('utf-8'),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, header[len(PREFIX):])
