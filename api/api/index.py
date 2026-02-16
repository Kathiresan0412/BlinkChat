"""
Vercel serverless entry: expose Django WSGI so all routes are handled by Django.
WebSockets will NOT work on Vercel (serverless is request/response only).
"""
import os
import sys

# Project root is the parent of this file's directory (api/)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from config.wsgi import application

# Vercel Python runtime looks for "app" (WSGI/ASGI)
app = application
