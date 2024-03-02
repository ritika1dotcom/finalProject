import itertools
import traceback
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings
import random
import numpy as np
from django.db.models import F
from users.models import PlayHistory, UserPreferences
from django.contrib.auth.models import User
from itertools import combinations
from django.http import JsonResponse
from .models import Feedback, Playlist, Track
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from users.views import preferences_view
from django.core.exceptions import ObjectDoesNotExist


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
            "song_title": track["name"],
            "artist_name": track["artists"][0]["name"],
            "album_name": track["album"]["name"],
            "album_image": album_image_url,
            "preview_url": track.get("preview_url"),
        }
        tracks.append(track_data)

    return render(request, 'search.html', {'tracks': tracks})

def fetch_music(request):
    # Define a list of keywords to search for in playlist names
    keywords = ['K-pop', 'Rock', 'Pop', 'Love Songs', 'Japanese', 'Nepali', 'Bollywood']

    for keyword in keywords:
        playlists = sp.search(q=keyword, type='playlist', limit=1)
        if not playlists['playlists']['items']:
            continue

        playlist_data = random.choice(playlists['playlists']['items'])
        playlist_uri = playlist_data['uri']
        playlist_name = playlist_data['name']

        all_tracks_data = sp.playlist_tracks(playlist_uri)["items"]
        selected_tracks_data = random.sample(all_tracks_data, min(len(all_tracks_data), 10))

        for track_data in selected_tracks_data:
            track = track_data["track"]
            
            artist_uri = track["artists"][0]["uri"]
            artist_info = sp.artist(artist_uri)
            album_image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None

            # Save track to the database only if preview_url is not None
            preview_url = track.get("preview_url")
            if preview_url:
                # Create a new playlist based on the keyword if it doesn't exist
                playlist, _ = Playlist.objects.get_or_create(name=keyword)
                
                # Save the track associated with the current playlist (keyword)
                new_track = Track.objects.create(
                    playlist=playlist,
                    name=track["name"],
                    artist_name=track["artists"][0]["name"],
                    artist_popularity=artist_info["popularity"],
                    artist_genres=artist_info["genres"],
                    album_name=track["album"]["name"],
                    track_popularity=track["popularity"],
                    album_image=album_image_url,
                    preview_url=preview_url
                )
                print(f"Keyword: {keyword}, Track: {new_track.name}, Artist: {new_track.artist_name}")
            else:
                print(f"Skipping track {track['name']} because preview_url is missing.")

    return redirect('admin:index')

def update_song_rating(request, username):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # print(data)
            song_data = data.get('data')
            if song_data:
                song_name = song_data.get('song_name')
                rating = song_data.get('rating')
                # print(song_name, rating)  # Output: Closer Than This 4
            else:
                print('No song data found in the request')

            # Update the rating of the song in the database
            if song_name and rating:
                try:
                    song = Track.objects.get(name=song_name)
                    # print(song)
                    song.rating = rating
                    song.save()
                    return JsonResponse({'success': True})
                except ObjectDoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Song does not exist'})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid data'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def featured_music(request):
    user_has_preferences = None
    form = None

    # Check if the user is authenticated before calling preferences_view
    if request.user.is_authenticated:
        user_has_preferences = preferences_view(request)
        form = user_has_preferences  # Now user_has_preferences is a form instance

    # Fetch all playlists from the database
    playlists = Playlist.objects.all()

    # Prepare data to be passed to the template
    playlists_data = []
    for playlist in playlists:
        # Fetch related tracks for each playlist
        all_tracks = playlist.track_set.all().values('name', 'artist_name', 'album_image', 'preview_url')
        # Select ten random tracks from all tracks
        selected_tracks = random.sample(list(all_tracks), min(len(all_tracks), 10))
        # Append playlist and tracks data as a dictionary to playlists_data list
        playlists_data.append({'playlist': playlist, 'tracks': selected_tracks})

    return render(request, 'home.html', {'featured_playlists': playlists_data, 'user_has_preferences': user_has_preferences, 'form': form})

def user_preferences_view(request, username):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        try:
            # Attempt to get the user's preferences
            user_preferences = UserPreferences.objects.get(user=request.user)

            # Extract relevant information
            age_group = user_preferences.age_group
            favorite_music_genre = user_preferences.favorite_music_genre

            # Generate random recommendations based on favorite music genre
            # recommendations = generate_random_recommendations(favorite_music_genre, 0.5)
            # matrix_recommendation = generate_random_matrix(favorite_music_genre, 0.5)
            # # Generate user song data based on age_group and favorite music genre
            # user_song_data = get_user_song_data(age_group, favorite_music_genre)

            # Return recommendations as JSON response
            return JsonResponse({'age_group': age_group, 'favorite_music_genre': favorite_music_genre})

        except UserPreferences.DoesNotExist:
            # Handle the case where the user doesn't have preferences
            return JsonResponse({'message': 'No preferences found.'})

    else:
        # Handle the case where the user is not authenticated
        return JsonResponse({'message': 'User not authenticated.'})


def get_all_songs(favorite_music_genres):
    all_music = {}

    # Ensure favorite_music_genres is a list
    if not isinstance(favorite_music_genres, list):
        # Split the string into a list using a delimiter (e.g., comma)
        favorite_music_genres = favorite_music_genres.split(',')

    # Remove leading and trailing whitespaces, square brackets, and single quotes
    favorite_music_genres = [genre.strip("[]' ") for genre in favorite_music_genres]

    # Debugging print to see the genres after stripping
    # print("Genres after stripping:", favorite_music_genres)

    for genre in favorite_music_genres:
        genre = genre.strip()  # Remove leading and trailing whitespaces

        try:
            # Query the database to get playlist based on the genre
            playlist = Playlist.objects.get(name=genre)

            # Query the database to get tracks related to the playlist
            tracks = Track.objects.filter(playlist=playlist)[:20]

            for track in tracks:
                all_music[track.name] = {
                    "name": track.name,
                    "artist_name": track.artist_name,
                    "artist_popularity": track.artist_popularity,
                    "artist_genres": track.artist_genres.split(','),  # Convert genres string to list
                    "album_name": track.album_name,
                    "track_popularity": track.track_popularity,
                    "album_image": track.album_image,
                    "preview_url": track.preview_url,
                    "rating": track.rating,
                }

        except Playlist.DoesNotExist:
            # Handle the case where the playlist doesn't exist
            print(f"Playlist with name '{genre}' does not exist.")
        # print(all_music)
    return all_music


def listening_history(user):
    # Fetch the listening history entries for the user
    user_history_entries = PlayHistory.objects.filter(user=user).order_by('date_played')

    # Create a list to represent the user's listening history with additional details
    user_history = [
        {
            "song_title": entry.song_title,
            "artist_name": entry.artist_name,  # Replace with the actual field name in your model
            "album_image": entry.album_image,
            "preview_url" : entry.preview_url,  # Replace with the actual field name in your model
        }
        for entry in user_history_entries
    ]

    # Convert the list of dictionaries to a list of tuples
    user_history_tuples = [
        (
            entry["song_title"],
            entry["artist_name"],
            entry["album_image"],
            entry["preview_url"],
        )
        for entry in user_history
    ]
    return user_history_tuples

def get_user_song_data(age_group, favorite_music_genre):
    # Fetch all users
    users = User.objects.all()

    # Create a dictionary to store the listening history
    user_song_data = {}

    # Iterate through each user
    for user in users:
        # Fetch the listening history entries for the user based on age_group
        if age_group == user.user_preferences.age_group:
            # Assuming that you have a relationship between User and UserPreferences
            user_history_entries = PlayHistory.objects.filter(user=user).values_list('song_title', 'artist_name', 'album_image', 'preview_url')

            # Convert the queryset of tuples to a set of tuples
            user_history_entries = {tuple(entry) for entry in user_history_entries}

            # Store the listening history in the dictionary
            user_song_data[user.username] = user_history_entries

    # print("songs", user_song_data)
    return user_song_data


def generate_random_recommendations(favorite_genre, min_confidence):
    # Generate a list of random songs with high confidence
    all_music = get_all_songs(favorite_genre)

    # Filter out songs with popularity below min_confidence
    high_popularity_songs = {song: details for song, details in all_music.items() if details['track_popularity'] >= min_confidence}

    # Sort the high_popularity_songs dictionary by popularity in descending order
    sorted_songs = sorted(high_popularity_songs.items(), key=lambda x: x[1]['track_popularity'], reverse=True)

    # Extract song names from sorted_songs
    random_recommendation = [song for song, details in sorted_songs]

    # Select a random subset of the top songs, limit to 10 songs or less
    num_recommendations = min(10, len(random_recommendation))
    random_recommendations = [{'song': song, 'song_details': all_music[song]} for song in random_recommendation[:num_recommendations]]
    return random_recommendations


def generate_random_matrix(favorite_genre,min_confidence):
    # Generate a list of random songs with high confidence
    all_music = get_all_songs(favorite_genre)
    random_songs = get_random_songs(all_music)
    random_matrix = random.sample(random_songs, min(10, len(random_songs)))
    random_recommendation_matrix = [{'song': song, 'song_details': all_music[song]} for song in random_matrix]
    return random_recommendation_matrix

def get_random_songs(all_music):
    # Extract song names from the featured tracks
    all_songs = list(all_music.keys())

    # Replace this with your logic to fetch random songs (e.g., from a database or API)
    return all_songs


def generate_frequent_itemsets(user_song_data, min_support):
    itemsets = {}

    # Count individual item occurrences and pairs of items
    for user_history in user_song_data.values():
        # Count individual items
        for song in user_history:
            if frozenset([song]) in itemsets:
                itemsets[frozenset([song])] += 1
            else:
                itemsets[frozenset([song])] = 1

        # Count pairs of items
        for pair in combinations(user_history, 2):
            if frozenset(pair) in itemsets:
                itemsets[frozenset(pair)] += 1
            else:
                itemsets[frozenset(pair)] = 1

    # Prune itemsets below the minimum support
    frequent_itemsets = {k: v for k, v in itemsets.items() if v >= min_support}

    return frequent_itemsets

def generate_association_rules(frequent_itemsets):
    rules = []

    # Generate association rules
    for itemset in frequent_itemsets.keys():
        # print(len(itemset))
        for size in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, size):
                consequent = itemset - frozenset(antecedent)
                # print("antecedent",consequent)
                support = frequent_itemsets[itemset]

                # Check if antecedent is not an empty set
                if antecedent:
                    confidence = support / frequent_itemsets.get(frozenset(antecedent), 1)
                    rules.append((frozenset(antecedent), consequent, support, confidence))

    return rules

def recommend_songs(song_data, association_rules, user_obj, sp):
    recommendations = []

    # Convert the user's listening history to a set of tuples
    user_listening_history = set(song_data[user_obj.username])

    for rule in association_rules:
        antecedent, consequent, support, confidence = rule

        # Check if the antecedent is in the user's listening history
        if antecedent.issubset(user_listening_history):
            # Filter out songs already in the listening history
            recommended_songs = list(consequent - user_listening_history)
            for song_tuple in recommended_songs:
                # Check if the song tuple is in the user's listening history
                if song_tuple in user_listening_history:
                    continue

                # Extract song title, artist_name, and album_image from the song tuple
                song_title, artist_name, album_image, _ = song_tuple

                # Make an API request to Spotify to get additional details including preview_url
                track_results = sp.search(q=f"{song_title} {artist_name}", type='track', limit=1)

                if track_results['tracks']['items']:
                    track = track_results['tracks']['items'][0]
                    preview_url = track.get('preview_url')

                    recommendations.append({
                        'song': song_title,
                        'confidence': confidence,
                        'song_details': {
                            'artist_name': artist_name,
                            'album_image': album_image,
                            'preview_url': preview_url,
                        },
                    })

    return recommendations


def fetch_preview_url(song_id):
    # Replace 'YOUR_SPOTIFY_API_KEY' with your actual Spotify API key
    spotify_api_key = sp

    # Make a request to Spotify API to get track details including preview_url
    url = f'https://api.spotify.com/v1/tracks/{song_id}'
    headers = {'Authorization': f'Bearer {spotify_api_key}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        track_data = response.json()
        preview_url = track_data.get('preview_url')
        return preview_url
    else:
        return None


def recommend_song(request, username):
    user_obj = get_object_or_404(User, username=username)
    min_support_threshold = 0.2
    min_confidence = 0.5
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

    # Fetch the listening history for the current user
    try:
        user_preferences = UserPreferences.objects.get(user=user_obj)
        age_group = user_preferences.age_group
        favorite_music_genre = user_preferences.favorite_music_genre
    except UserPreferences.DoesNotExist:
        # Handle the case where the user doesn't have preferences
        age_group = None
        favorite_music_genre = None

    user_listening_history = listening_history(user_obj)
    song_data = get_user_song_data(age_group, favorite_music_genre)
    data = get_user_song_list()
    frequent_itemsets = generate_frequent_itemsets(song_data, min_support_threshold)
    association_rule = generate_association_rules(frequent_itemsets)
    recommendations = recommend_songs(song_data, association_rule,user_obj,sp)
    random_songs = random.sample(recommendations, min(10, len(recommendations)))
    matrix = recommend(user_obj,data)
    # print("matrix",favorite_music_genre)

    # If there are no recommendations, generate a random playlist
    if not recommendations:
        song = generate_random_recommendations(favorite_music_genre , min_confidence)
        random_recommendation_matrix = generate_random_matrix(favorite_music_genre ,min_confidence)
        # print("song",song)
        context = {
            'user_obj': user_obj,
            'recommended_songs': song,
            'random_recommendation_matrix' : random_recommendation_matrix,
        
        }
    else:
        context = {
            'user_obj': user_obj,
            'recommendations': random_songs,
            'matrix': matrix['recommended_songs'],
        }

    return render(request, 'collections.html', context)


def get_user_song_list():
    # Fetch all users
    users = User.objects.all()

    # Create lists to store user, song, and play count data
    user_ids = []
    song_ids = []
    play_counts = []
    song_titles = []  # New list for song titles
    user_names = []   # New list for user names
    artist_name = []
    album_image = []
    preview_url = []

    # Create dictionaries to map usernames and song details to unique numerical identifiers
    user_id_mapping = {}
    song_id_mapping = {}
    user_song_mapping = {}  # New dictionary to track user-song combinations

    user_counter = 1
    song_counter = 1

    # Iterate through each user
    for user in users:
        # Fetch the listening history entries for the user
        user_history_entries = PlayHistory.objects.filter(user=user)

        # Iterate through each song entry in the user's history
        for song_entry in user_history_entries:
            # Get or assign a unique numerical identifier for the user
            user_id = user_id_mapping.setdefault(user.username, user_counter)
            if user_id == user_counter:
                user_counter += 1

            # Get or assign a unique numerical identifier for the song
            song_id = song_id_mapping.setdefault(song_entry.song_title, song_counter)
            if song_id == song_counter:
                song_counter += 1

            # Check if the user-song combination already exists
            user_song_key = (user_id, song_id)
            if user_song_key in user_song_mapping:
                # Increment the play count
                play_counts[user_song_mapping[user_song_key]] += 1
            else:
                # Append data to the lists
                user_ids.append(user_id)
                song_ids.append(song_id)
                play_counts.append(1)  # Assuming each play is counted once
                song_titles.append(song_entry.song_title)
                artist_name.append(song_entry.artist_name)
                album_image.append(song_entry.album_image)
                user_names.append(user.username)
                preview_url.append(song_entry.preview_url)

                # Update the user-song mapping
                user_song_mapping[user_song_key] = len(user_ids) - 1

    # Create a DataFrame from the lists
    data = pd.DataFrame({
        'user_id': user_ids,
        'song_id': song_ids,
        'play_count': play_counts,
        'song_title': song_titles,  # Add song titles to the DataFrame
        'user_name': user_names,     # Add user names to the DataFrame
        'artist_name': artist_name,
        'album_image': album_image,
        'preview_url' : preview_url,

    })
    return data

def matrix_factorization(data, num_users, num_songs, num_factors, num_iterations, learning_rate):
    # Initialize user and item matrices randomly
    user_matrix = np.random.rand(num_users, num_factors)
    song_matrix = np.random.rand(num_factors, num_songs)

    # Perform matrix factorization using stochastic gradient descent
    for iteration in range(num_iterations):
        for i in range(len(data)):
            user_id = data['user_id'][i] - 1  # Adjusting index
            song_id = data['song_id'][i] - 1  # Adjusting index
            play_count = data['play_count'][i]

            # Calculate predicted play count
            prediction = np.dot(user_matrix[user_id, :], song_matrix[:, song_id])

            # Update user and song matrices using gradient descent
            user_matrix[user_id, :] += learning_rate * (play_count - prediction) * song_matrix[:, song_id]
            song_matrix[:, song_id] += learning_rate * (play_count - prediction) * user_matrix[user_id, :]

    return user_matrix, song_matrix


def recommend(username,data):
    user_obj = get_object_or_404(User, username=username)

    # Assuming num_users, num_songs, num_factors, num_iterations, and learning_rate are set appropriately
    num_users = len(data['user_id'].unique())
    num_songs = len(data['song_id'].unique())
    num_factors = 5  # Adjust as needed
    num_iterations = 50  # Adjust as needed
    learning_rate = 0.01  # Adjust as needed

    user_matrix, song_matrix = matrix_factorization(data, num_users, num_songs, num_factors, num_iterations, learning_rate)

    # Make recommendations for a user (replace user_id_to_recommend with the actual user you want recommendations for)
    user_id_to_recommend = 1
    user_recommendations = np.dot(user_matrix[user_id_to_recommend - 1, :], song_matrix)
    k = 10
    # Get indices of top recommended songs
    top_song_indices = np.argsort(user_recommendations)[::-1][:k]  # k is the number of top recommendations

    # Extract song IDs, titles, artist names, and album images
    recommended_song_ids = top_song_indices + 1  # Adjusting index
    recommended_song_details = [
        {
            'song_id': song_id,
            'song_title': data[data['song_id'] == song_id]['song_title'].iloc[0],
            'artist_name': data[data['song_id'] == song_id]['artist_name'].iloc[0],  # Assuming you have 'artist_name' column
            'album_image': data[data['song_id'] == song_id]['album_image'].iloc[0],  # Assuming you have 'album_image' column
            'preview_url': fetch_preview_url(song_id),   # Assuming you have 'album_image' column
        }
        for song_id in recommended_song_ids
    ]

    # print("Recommended Song Details:", recommended_song_details)

    # Convert DataFrame to a list of dictionaries for easier rendering in Django templates
    user_song_list = data.to_dict('records')
    context = {
        'user_song_list' : user_song_list,
        'recommended_songs': recommended_song_details,

    }
    return context


@csrf_exempt
@login_required  # Decorator to ensure the user is authenticated
def submit_feedback(request, username):
    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(data)
            
            # Extract values from data
            algorithm = data.get('data', {}).get('algorithm')
            user_age_group = data.get('data', {}).get('user_age_group')
            user_favorite_genre = data.get('data', {}).get('user_favorite_genre')

            # Create Feedback instance and save to the database
            feedback = Feedback.objects.create(
                user=user,
                algorithm=algorithm,
                user_age_group_field=user_age_group,
                user_favorite_genre_field=user_favorite_genre,
            )
            print(feedback, "feedback")
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except Exception as e:
            # Log the exception
            print(f"Error processing feedback: {e}")
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': 'Error processing feedback'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def chart(request):
    print('Chart view called')
    # Aggregate feedback data for all users and algorithms
    feedback_data = Feedback.objects.annotate(
        user_age_group=F('user__user_preferences__age_group'),
        user_favorite_genre=F('user__user_preferences__favorite_music_genre')
    ).values('user__username', 'algorithm', 'user_age_group', 'user_favorite_genre', 'feedback_date')  # Include feedback date

    feedback_data_list = list(feedback_data)

    return JsonResponse({'feedback_data': feedback_data_list}, safe=False)

def chart_page(request):
    # Get the JSON data from the other view
    json_data = chart(request).content.decode('utf-8')

    # Parse the JSON string into a Python object
    feedback_data = json.loads(json_data)['feedback_data']

    # Convert boolean values to lowercase strings and handle user_age_group and user_favorite_genre
    transformed_data = [
        {
            'user__username': entry['user__username'],
            'algorithm': entry['algorithm'],
            'user_age_group': entry['user_age_group'] if entry['user_age_group'] else "Unknown",
            'user_favorite_genre': entry['user_favorite_genre'] if entry['user_favorite_genre'] else "Unknown",
            'feedback_date': entry['feedback_date'],
        }
        for entry in feedback_data
    ]

    return render(request, 'chart.html', {'json_data': transformed_data})