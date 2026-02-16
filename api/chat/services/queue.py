"""
Redis-based random matchmaking queue.
"""
import json
import uuid
import logging
import time
from django.conf import settings
import redis

logger = logging.getLogger(__name__)

QUEUE_KEY = 'blinkchat:matchmaking:queue'
SESSION_PREFIX = 'blinkchat:session:'
SESSION_TTL = 3600  # 1 hour


class MatchmakingQueue:
    def __init__(self):
        self._redis = redis.from_url(getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379'))

    def join(self, channel_name: str, user_id: str, meta: dict = None) -> str | None:
        """
        Add user to queue. If someone is waiting, pop them and return session_id.
        Otherwise add current user to queue and return None.
        """
        meta = meta or {}
        payload = {'channel_name': channel_name, 'user_id': str(user_id), 'meta': meta}
        # Try to pop a waiting user (FIFO for fairness)
        raw = self._redis.lpop(QUEUE_KEY)
        if raw:
            try:
                other = json.loads(raw)
                session_id = str(uuid.uuid4())
                started_at = time.time()
                self._redis.setex(
                    f'{SESSION_PREFIX}{session_id}',
                    SESSION_TTL,
                    json.dumps({
                        'session_id': session_id,
                        'user1': other,
                        'user2': payload,
                        'started_at': started_at,
                    })
                )
                return session_id
            except (json.JSONDecodeError, TypeError):
                pass
        self._redis.rpush(QUEUE_KEY, json.dumps(payload))
        return None

    def leave_queue(self, channel_name: str) -> None:
        """Remove this channel from the queue (e.g. on disconnect)."""
        raw_list = self._redis.lrange(QUEUE_KEY, 0, -1)
        new_list = []
        for raw in raw_list or []:
            try:
                data = json.loads(raw)
                if data.get('channel_name') != channel_name:
                    new_list.append(raw)
            except (json.JSONDecodeError, TypeError):
                new_list.append(raw)
        self._redis.delete(QUEUE_KEY)
        for item in new_list:
            self._redis.rpush(QUEUE_KEY, item)

    def get_session(self, session_id: str) -> dict | None:
        raw = self._redis.get(f'{SESSION_PREFIX}{session_id}')
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

    def delete_session(self, session_id: str) -> None:
        self._redis.delete(f'{SESSION_PREFIX}{session_id}')


matchmaking_queue = MatchmakingQueue()
