from django.core.management.base import BaseCommand
from spotify.models import Track
from django.db import models


class Command(BaseCommand):
    help = 'Deletes duplicate songs from the Track model'

    def handle(self, *args, **kwargs):
        # Identify duplicate songs based on criteria (e.g., name and artist_name)
        duplicate_songs = (Track.objects.values('name', 'artist_name')
                                    .annotate(count=models.Count('id'))
                                    .filter(count__gt=1))

        # Loop through duplicate songs and keep one record while deleting the rest
        for song in duplicate_songs:
            # Get duplicate song instances
            duplicate_instances = Track.objects.filter(name=song['name'], artist_name=song['artist_name']).order_by('-rating_count')
            # Keep the first instance (highest rating_count) and delete the rest
            first_instance = duplicate_instances.first()
            duplicate_instances.exclude(id=first_instance.id).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted duplicates for song: {first_instance.name} - {first_instance.artist_name}"))
