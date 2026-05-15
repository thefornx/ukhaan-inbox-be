import redis
from django.conf import settings

RedisClient = redis.Redis(
    host=settings.REDIS.get('HOST'),
    port=settings.REDIS.get('PORT'),
    db=settings.REDIS.get('DB'),
    password=settings.REDIS.get('PASSWORD'),
    decode_responses=True
)