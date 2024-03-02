# models.py
from django.db import models
from django.contrib.auth.models import User
from users.models import UserPreferences

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=20)  # Change the max_length as needed
    feedback_date = models.DateTimeField(auto_now_add=True)
    
    user_age_group_field = models.CharField(max_length=10, null=True, blank=True)  # Adjust max_length as needed
    user_favorite_genre_field = models.CharField(max_length=255, null=True, blank=True)  # Adjust max_length as needed

    def user_age_group(self):
        # Access the current user's age group through the UserPreferences
        try:
            return self.user.user_preferences.age_group
        except UserPreferences.DoesNotExist:
            return "Unknown"

    def user_favorite_genre(self):
        # Access the current user's favorite music genre through the UserPreferences
        try:
            return self.user.user_preferences.favorite_music_genre
        except UserPreferences.DoesNotExist:
            return "Unknown"

class Playlist(models.Model):
    name = models.CharField(max_length=255)

class Track(models.Model):
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    artist_popularity = models.IntegerField()
    artist_genres = models.TextField()  # You might want to consider using a separate Genre model if genres can be multiple.
    album_name = models.CharField(max_length=255)
    track_popularity = models.IntegerField()
    album_image = models.URLField()
    preview_url = models.URLField(null=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0) 

    def __str__(self):
        return f"{self.name} by {self.artist_name}"
