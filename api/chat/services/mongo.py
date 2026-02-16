"""
MongoDB service for match logs and optional storage.
"""
import os
from pymongo import MongoClient
from pymongo.database import Database

_client = None


def get_mongo_db() -> Database:
    global _client
    if _client is None:
        uri = os.environ.get('MONGO_URI', 'mongodb://127.0.0.1:27017')
        db_name = os.environ.get('MONGO_DB_NAME', 'blinkchat')
        _client = MongoClient(uri)
        return _client[db_name]
    return _client[os.environ.get('MONGO_DB_NAME', 'blinkchat')]


def log_match(session_id: str, user_ids: list, started_at: str, ended_at: str = None):
    """Store match event in MongoDB (optional, non-blocking)."""
    try:
        db = get_mongo_db()
        db.matches.insert_one({
            'session_id': session_id,
            'user_ids': user_ids,
            'started_at': started_at,
            'ended_at': ended_at,
        })
    except Exception:
        pass  # Don't fail request if MongoDB is down
