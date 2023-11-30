from django.db import models

class Track(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)    # Add other fields as needed
# yourapp/models.py
from django.db import models

class PopTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Pop genre

class RockTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Rock genre

class HipHopTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Hip-Hop genre

class NepaliTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Hip-Hop genre

class HindiTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Hip-Hop genre

class EnglishTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Hip-Hop genre

class KoreanTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Hip-Hop genre

class JapaneseTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Hip-Hop genre

class ChineseTrack(models.Model):
    uri = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_image = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    # Add other fields specific to Hip-Hop genre