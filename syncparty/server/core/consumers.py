import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

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