"""
WebSocket consumer: matchmaking, text chat, and WebRTC signaling.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser

from chat.services.queue import matchmaking_queue
from chat.services.mongo import log_match
from chat.models import UserProfile

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_profile(user):
    if not user or user.is_anonymous:
        return None
    try:
        p = UserProfile.objects.get(user=user)
        return {'user_id': user.id, 'username': user.username, 'display_name': p.display_name or user.username}
    except UserProfile.DoesNotExist:
        return {'user_id': user.id, 'username': user.username, 'display_name': user.username}
    except Exception:
        return {'user_id': user.id, 'username': str(user), 'display_name': str(user)}


@database_sync_to_async
def is_user_banned(user):
    if not user or user.is_anonymous:
        return False
    try:
        return UserProfile.objects.get(user=user).is_banned
    except UserProfile.DoesNotExist:
        return False
    except Exception:
        return True


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.partner_channel = None
        self.user_id = None

    async def connect(self):
        self.room_group_name = None
        user = self.scope.get('user') or AnonymousUser()
        if await is_user_banned(user):
            await self.close(code=4003)
            return
        self.user_id = getattr(user, 'id', None) or f'anonymous_{id(self)}'
        await self.accept()

        # Optional: send auth info
        profile = await get_user_profile(user)
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'user': profile,
        }))

        # Join matchmaking queue (sync Redis calls in thread)
        session_id = await sync_to_async(matchmaking_queue.join)(
            self.channel_name,
            self.user_id,
            meta=profile or {}
        )
        if session_id:
            session = await sync_to_async(matchmaking_queue.get_session)(session_id)
            if session:
                user1 = session['user1']
                user2 = session['user2']
                self.session_id = session_id
                self.partner_channel = user2['channel_name'] if user1['channel_name'] == self.channel_name else user1['channel_name']
                self.room_group_name = f'session_{session_id}'
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
                # Notify the other user (who was waiting) via direct channel send
                other_channel = user2['channel_name'] if user1['channel_name'] == self.channel_name else user1['channel_name']
                await self.channel_layer.send(other_channel, {
                    'type': 'matched_from_queue',
                    'session_id': session_id,
                    'room_group_name': self.room_group_name,
                    'partner': user2 if user1['channel_name'] == self.channel_name else user1,
                    'is_initiator': True,
                })
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'session_matched',
                    'session_id': session_id,
                    'user1': user1,
                    'user2': user2,
                })
                await sync_to_async(log_match)(session_id, [str(user1.get('user_id')), str(user2.get('user_id'))], str(session.get('started_at', '')), None)
                return
        await self.send(text_data=json.dumps({'type': 'waiting', 'message': 'Looking for someone...'}))

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'partner_left',
                'channel': self.channel_name,
            })
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            if self.session_id:
                await sync_to_async(matchmaking_queue.delete_session)(self.session_id)
        else:
            await sync_to_async(matchmaking_queue.leave_queue)(self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        msg_type = data.get('type')
        if msg_type == 'chat':
            if self.room_group_name:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'chat_message',
                    'channel': self.channel_name,
                    'message': data.get('message', ''),
                    'sender_id': self.user_id,
                })
        elif msg_type == 'signal':
            if self.room_group_name:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'webrtc_signal',
                    'channel': self.channel_name,
                    'payload': data.get('payload'),
                })
        elif msg_type == 'next':
            if self.room_group_name:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'user_next',
                    'channel': self.channel_name,
                })

    async def matched_from_queue(self, event):
        """Called when we were in queue and someone matched with us (we are initiator for WebRTC)."""
        self.session_id = event['session_id']
        self.room_group_name = event['room_group_name']
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            'type': 'matched',
            'session_id': event['session_id'],
            'partner': event['partner'],
            'is_initiator': event.get('is_initiator', True),
        }))

    async def session_matched(self, event):
        is_initiator = event['user1']['channel_name'] == self.channel_name
        await self.send(text_data=json.dumps({
            'type': 'matched',
            'session_id': event['session_id'],
            'partner': event['user2'] if is_initiator else event['user1'],
            'is_initiator': is_initiator,
        }))

    async def chat_message(self, event):
        if event['channel'] == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'sender_id': event['sender_id'],
        }))

    async def webrtc_signal(self, event):
        if event['channel'] == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            'type': 'signal',
            'payload': event['payload'],
        }))

    async def user_next(self, event):
        if event['channel'] == self.channel_name:
            return
        await self.send(text_data=json.dumps({'type': 'partner_next'}))

    async def partner_left(self, event):
        await self.send(text_data=json.dumps({'type': 'partner_left'}))
