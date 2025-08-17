from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Party, PartyDevice, PlaybackState
from .serializers import UserSerializer, PartySerializer, PartyDeviceSerializer, PlaybackStateSerializer


class RegisterView(generics.CreateAPIView):
	serializer_class = UserSerializer
	permission_classes = [permissions.AllowAny]


class PartyViewSet(viewsets.ModelViewSet):
	queryset = Party.objects.all().order_by('-created_at')
	serializer_class = PartySerializer

	def get_queryset(self):
		return Party.objects.filter(host=self.request.user)

	def perform_create(self, serializer):
		party = serializer.save(host=self.request.user)
		PlaybackState.objects.create(party=party)

	@action(detail=False, methods=['get'], url_path='by-code/(?P<code>[^/.]+)')
	def by_code(self, request, code=None):
		party = get_object_or_404(Party, code=code.upper())
		self.check_object_permissions(request, party)
		# Allow any authenticated to fetch party info
		return Response(PartySerializer(party).data)

	@action(detail=False, methods=['post'], url_path='join-by-code')
	def join_by_code(self, request):
		code = request.data.get('code', '')
		label = request.data.get('label', request.user.username)
		party = get_object_or_404(Party, code=code.upper())
		device, _ = PartyDevice.objects.get_or_create(party=party, user=request.user, defaults={'label': label})
		device.connected = True
		device.label = label
		device.save()
		return Response(PartySerializer(party).data)

	@action(detail=True, methods=['post'])
	def join(self, request, pk=None):
		party = self.get_object()
		label = request.data.get('label', request.user.username)
		device, _ = PartyDevice.objects.get_or_create(party=party, user=request.user, defaults={'label': label})
		device.connected = True
		device.label = label
		device.save()
		return Response(PartySerializer(party).data)

	@action(detail=True, methods=['post'])
	def leave(self, request, pk=None):
		party = self.get_object()
		PartyDevice.objects.filter(party=party, user=request.user).update(connected=False)
		return Response({'status': 'left'})

	@action(detail=True, methods=['post'])
	def update_device(self, request, pk=None):
		party = self.get_object()
		device = get_object_or_404(PartyDevice, party=party, user=request.user)
		serializer = PartyDeviceSerializer(device, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)

	@action(detail=True, methods=['post'])
	def playback(self, request, pk=None):
		party = self.get_object()
		playback = party.playback
		serializer = PlaybackStateSerializer(playback, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)
