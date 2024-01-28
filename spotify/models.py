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
