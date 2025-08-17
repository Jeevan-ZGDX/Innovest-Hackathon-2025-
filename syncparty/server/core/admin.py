from django.contrib import admin
from .models import Party, PartyDevice, PlaybackState

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'host', 'is_active', 'created_at')
	search_fields = ('code', 'name', 'host__username')

@admin.register(PartyDevice)
class PartyDeviceAdmin(admin.ModelAdmin):
	list_display = ('party', 'user', 'label', 'grid_x', 'grid_y', 'is_main_device', 'connected', 'last_seen')
	list_filter = ('party', 'connected')

@admin.register(PlaybackState)
class PlaybackStateAdmin(admin.ModelAdmin):
	list_display = ('party', 'track_uri', 'position_ms', 'is_playing', 'updated_at')
