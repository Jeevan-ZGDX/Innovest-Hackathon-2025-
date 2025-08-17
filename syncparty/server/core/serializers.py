from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Party, PartyDevice, PlaybackState


class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)

	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'password']

	def create(self, validated_data):
		user = User(username=validated_data['username'], email=validated_data.get('email', ''))
		user.set_password(validated_data['password'])
		user.save()
		return user


class PartyDeviceSerializer(serializers.ModelSerializer):
	user = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model = PartyDevice
		fields = ['id', 'party', 'user', 'label', 'grid_x', 'grid_y', 'angle_deg', 'is_main_device', 'connected', 'last_seen']
		read_only_fields = ['connected', 'last_seen']


class PlaybackStateSerializer(serializers.ModelSerializer):
	class Meta:
		model = PlaybackState
		fields = ['track_uri', 'position_ms', 'is_playing', 'updated_at']


class PartySerializer(serializers.ModelSerializer):
	devices = PartyDeviceSerializer(many=True, read_only=True)
	playback = PlaybackStateSerializer(read_only=True)

	class Meta:
		model = Party
		fields = ['id', 'code', 'host', 'name', 'created_at', 'is_active', 'devices', 'playback']
		read_only_fields = ['code', 'host', 'created_at', 'devices', 'playback']