from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings
import random
from users.models import PlayHistory
from django.contrib.auth.models import User
from itertools import chain, combinations
import time

# Fetch client credentials from settings
SPOTIPY_CLIENT_ID = settings.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = settings.SPOTIPY_CLIENT_SECRET

# Initialize spotipy with your client id and secret
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Create your views here.
# Create your views here.

def show_base(request):
    return render(request, 'landing.html')

def search_song(request):
    query = request.GET.get('query')
    # Start with song search
    song_results = sp.search(q=query, type='track', limit=10)
    tracks = []

    for track in song_results['tracks']['items']:
        # Extract the album image URL
        album_image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None

        # Add the track details to the list
        track_data = {
            "song_name": track["name"],
            "artist_name": track["artists"][0]["name"],
            "album_name": track["album"]["name"],
            "album_image": album_image_url,
            "preview_url": track.get("preview_url"),
        }
        tracks.append(track_data)

    return render(request, 'search.html', {'tracks': tracks})

import random

def featured_music(request):
    # Define a list of keywords to search for in playlist names
    keywords = ['Nepali', 'Bollywood', 'K-pop', 'Chinese', 'Japanese', 'Hollywood']

    # Fetch playlists for each keyword
    featured_playlists = []
    for keyword in keywords:
        # Fetch a list of featured playlists for the current keyword
        playlists = sp.search(q=keyword, type='playlist', limit=5)

        # If no playlists were found for the keyword, skip to the next one
        if not playlists['playlists']['items']:
            continue

        # Extract essential details for each playlist
        playlist_data = random.choice(playlists['playlists']['items'])
        playlist_uri = playlist_data['uri']
        playlist_name = playlist_data['name']

        # Fetch all tracks from the selected playlist
        all_tracks_data = sp.playlist_tracks(playlist_uri)["items"]

        # Randomly select 10 tracks from all tracks
        selected_tracks_data = random.sample(all_tracks_data, min(10, len(all_tracks_data)))

        # Extract essential details for each selected track in the playlist
        featured_tracks = []
        for track_data in selected_tracks_data:
            track = track_data["track"]
            
            # Get the track's main artist's details
            artist_uri = track["artists"][0]["uri"]
            artist_info = sp.artist(artist_uri)
            album_image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None

            featured_tracks.append({
                "uri": track["uri"],
                "name": track["name"],
                "artist_name": track["artists"][0]["name"],
                "artist_popularity": artist_info["popularity"],
                "artist_genres": artist_info["genres"],
                "album_name": track["album"]["name"],
                "track_popularity": track["popularity"],
                "album_image": album_image_url,
                "preview_url": track.get("preview_url") 
            })

        # Add the playlist details along with its tracks to the featured_playlists list
        featured_playlists.append({
            "playlist_name": playlist_name,
            "tracks": featured_tracks,
        })
        print('featured', featured_playlists);

    return render(request, 'home.html', {'featured_playlists': featured_playlists})
