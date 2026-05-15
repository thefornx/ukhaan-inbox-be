from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from django.conf import settings

from core.provider.redis import RedisClient


class Authentication:
    redis_key_prefix = 'auth:access:'

    def __init__(self):
        self.secret = settings.JWT.get('SECRET')
        self.algorithm = settings.JWT.get('ALGORITHM')
        self.ttl = settings.JWT.get('ACCESS_TOKEN_TTL')

    def generate(self, user_id):
        jti = uuid4().hex
        now = datetime.now(timezone.utc)

        payload = {
            'sub': str(user_id),
            'jti': jti,
            'iat': now,
            'exp': now + timedelta(seconds=self.ttl),
        }

        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        RedisClient.set(self.redis_key_prefix + jti, str(user_id), ex=self.ttl)

        return token

    def verify(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.PyJWTError:
            return None

        jti = payload.get('jti')
        user_id = RedisClient.get(self.redis_key_prefix + jti) if jti else None

        if user_id is None:
            return None

        return int(user_id)

    def revoke(self, token):
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={'verify_exp': False},
            )
        except jwt.PyJWTError:
            return False

        jti = payload.get('jti')
        if not jti:
            return False

        return bool(RedisClient.delete(self.redis_key_prefix + jti))
