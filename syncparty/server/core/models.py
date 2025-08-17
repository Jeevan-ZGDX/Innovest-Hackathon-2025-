from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


class Party(models.Model):
	code = models.CharField(max_length=8, unique=True, db_index=True)
	host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_parties')
	name = models.CharField(max_length=100, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	def save(self, *args, **kwargs):
		if not self.code:
			self.code = get_random_string(8).upper()
		return super().save(*args, **kwargs)

	def __str__(self) -> str:
		return f"Party {self.code}"


class PartyDevice(models.Model):
	party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='devices')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='party_devices')
	label = models.CharField(max_length=100)
	grid_x = models.IntegerField(default=0)
	grid_y = models.IntegerField(default=0)
	angle_deg = models.FloatField(default=0.0)
	is_main_device = models.BooleanField(default=False)
	connected = models.BooleanField(default=False)
	last_seen = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('party', 'user')

	def __str__(self) -> str:
		return f"{self.label} ({self.user_id})"


class PlaybackState(models.Model):
	party = models.OneToOneField(Party, on_delete=models.CASCADE, related_name='playback')
	track_uri = models.CharField(max_length=512, blank=True)
	position_ms = models.BigIntegerField(default=0)
	is_playing = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"PlaybackState({self.party.code})"
