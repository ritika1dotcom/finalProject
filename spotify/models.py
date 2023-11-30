from django.db import models

class Track(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    # Add other fields as needed
