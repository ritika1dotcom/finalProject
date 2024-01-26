# models.py
from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=20)  # Change the max_length as needed
    feedback_date = models.DateTimeField(auto_now_add=True)
    
    genre = models.BooleanField(default=False)
    mood = models.BooleanField(default=False)
    new_music = models.BooleanField(default=False)
    artists = models.BooleanField(default=False)
    nostalgia = models.BooleanField(default=False)
