# yourapp/management/commands/fetch_spotipy_data.py
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.core.management.base import BaseCommand
from finalProject import settings
from spotify.models import Track, PopTrack, HindiTrack, HipHopTrack, ChineseTrack, NepaliTrack, JapaneseTrack, RockTrack

SPOTIPY_CLIENT_ID = settings.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = settings.SPOTIPY_CLIENT_SECRET

class Command(BaseCommand):
    help = 'Fetch and store random Spotify tracks for multiple genres and countries'

    def handle(self, *args, **options):
        # Spotipy authentication
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

        # Fetch available genres from Spotipy
        available_genres = sp.recommendation_genre_seeds()['genres']

        # Define models for each genre
        genre_model_mapping = [
            (genre.lower(), self.get_model_for_genre(genre.lower()))
            for genre in available_genres
        ]

        for genre, model in genre_model_mapping:
            # Fetch random tracks from a random playlist in the genre
            random_tracks_data = self.fetch_random_tracks(sp, genre)
            
            # Store tracks using the corresponding model
            self.store_tracks(model, random_tracks_data, f'Random {genre.capitalize()} Songs')

        self.stdout.write(self.style.SUCCESS('Random tracks fetched and stored successfully'))

    def fetch_random_tracks(self, sp, genre):
        # Fetch tracks from a random playlist in the specified genre
        playlists = sp.category_playlists(category_id=genre, limit=50)  # You can adjust the limit as needed

        if playlists and 'playlists' in playlists and 'items' in playlists['playlists']:
            random_playlist = random.choice(playlists['playlists']['items'])
            playlist_id = random_playlist['id']
            return sp.playlist_tracks(playlist_id)["items"]
        return []

    def store_tracks(self, model, tracks_data, genre):
        for track_data in tracks_data:
            uri = track_data['track']['uri']
            popularity = track_data['track']['popularity'] if 'popularity' in track_data['track'] else 0  # Default to 0 if popularity is not available

            # Check if a track with the same URI already exists
            if not model.objects.filter(uri=uri).exists():
                model.objects.create(
                    uri=uri,
                    name=track_data['track']['name'],
                    artist_name=track_data['track']['artists'][0]['name'],
                    album_name=track_data['track']['album']['name'],
                    album_image=track_data['track']['album']['images'][0]['url'] if track_data['track']['album']['images'] else None,
                    preview_url=track_data['track'].get('preview_url'),
                    popularity=popularity,
                    # Add other fields specific to the genre
                )
        self.stdout.write(self.style.SUCCESS(f'{genre} tracks fetched and stored'))

    def get_model_for_genre(self, genre):
        # Define models for each genre
        genre_model_mapping = {
            'classical': Track,
            'pop': PopTrack,
            'desi pop': HindiTrack,
            'hiphop': HipHopTrack,
            'chinese': ChineseTrack,
            'nepali indie': NepaliTrack,
            'japanese': JapaneseTrack,
            'rock': RockTrack,
            # Add more genres and models as needed
        }

        return genre_model_mapping.get(genre, Track)  # Default to Track if the genre is not found
