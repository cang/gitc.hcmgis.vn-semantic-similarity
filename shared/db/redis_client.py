import redis
import threading
from shared.core.config import settings

_redis = None
_lock = threading.Lock()

def get_redis():
    global _redis

    if _redis is None:
        with _lock:
            if _redis is None:
                print(f"Connect to Redis {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                _redis = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                    decode_responses=True
                )
    return _redis

def reset_redis():
    global _redis
    _redis = None
