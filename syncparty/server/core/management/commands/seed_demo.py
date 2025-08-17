from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Party, PartyDevice, PlaybackState


class Command(BaseCommand):
	help = 'Create demo data for SyncParty'

	def handle(self, *args, **options):
		User = get_user_model()
		user, _ = User.objects.get_or_create(username='demo')
		user.set_password('demo')
		user.save()
		party, _ = Party.objects.get_or_create(host=user, name='Demo Party')
		PlaybackState.objects.get_or_create(party=party)
		PartyDevice.objects.get_or_create(party=party, user=user, defaults={'label': 'Main Device', 'is_main_device': True})
		self.stdout.write(self.style.SUCCESS(f'Demo party ready: code={party.code} username=demo password=demo'))