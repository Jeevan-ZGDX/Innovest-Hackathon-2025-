import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
import time

from .models import Party, PartyDevice


class PartyConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.party_code = self.scope['url_route']['kwargs']['party_code']
		self.group_name = f"party_{self.party_code}"
		await self.channel_layer.group_add(self.group_name, self.channel_name)
		await self.accept()

	async def disconnect(self, code):
		await self.channel_layer.group_discard(self.group_name, self.channel_name)

	async def receive_json(self, content, **kwargs):
		message_type = content.get('type')
		if message_type == 'ping':
			await self.send_json({'type': 'pong'})
			return

		if message_type == 'time_sync':
			client_sent_at = content.get('clientSentAt')
			server_now_ms = int(time.time() * 1000)
			await self.send_json({'event': 'time_sync', 'serverNowMs': server_now_ms, 'clientSentAt': client_sent_at})
			return

		if message_type == 'device_update':
			await self.channel_layer.group_send(self.group_name, {
				'type': 'broadcast',
				'payload': {'event': 'device_update', 'data': content.get('data', {})}
			})
			return

		if message_type in ['play', 'pause', 'seek', 'track', 'ring']:
			await self.channel_layer.group_send(self.group_name, {
				'type': 'broadcast',
				'payload': {'event': message_type, 'data': content.get('data', {})}
			})
			return

	async def broadcast(self, event):
		await self.send_json(event['payload'])