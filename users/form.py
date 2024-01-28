# form.py
from django import forms
from .models import UserPreferences

class PreferencesForm(forms.ModelForm):
    AGE_CHOICES = [
        ('14-20', '14-20'),
        ('20-30', '20-30'),
        ('30-40', '30-40'),
        ('40-50', '40-50'),
        ('50+', '50+'),
    ]

    MUSIC_GENRE_CHOICES = [
        ('Rock', 'Rock'),
        ('Pop', 'Pop'),
        ('Japanese', 'Japanese'),
        ('Chinese', 'Chinese'),
        ('K-Pop', 'Korean'),
        ('Nepali', 'Nepali'),
        ('Love Songs', 'Romance'),
        # Add more choices as needed
    ]

    age_group = forms.ChoiceField(choices=AGE_CHOICES, widget=forms.Select(attrs={'class': 'border rounded w-full py-2 px-3 text-black bg-gray-300 focus:outline-none focus:border-blue-500'}))
    favorite_music_genre = forms.MultipleChoiceField(choices=MUSIC_GENRE_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'text-gray-300'}))

    class Meta:
        model = UserPreferences
        fields = ['age_group', 'favorite_music_genre']
