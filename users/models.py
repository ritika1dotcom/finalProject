from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    # Other song attributes if necessary

class PlayHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song_title = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    album_image = models.URLField(max_length=500, null=True, blank=True)  # Allow null and blank for album_image
    preview_url = models.URLField(max_length=500, null=True, blank=True)
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.album_image:
            return f"{self.song_title} by {self.artist_name} ({self.album_image})"
        else:
            return f"{self.song_title} by {self.artist_name} (No album image)"
        
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_preferences', unique=True)
    age_group = models.CharField(max_length=50)
    favorite_music_genre = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/images/')