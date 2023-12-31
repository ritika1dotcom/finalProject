import itertools
from django.shortcuts import get_object_or_404, render
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings
import random
import numpy as np
from users.models import PlayHistory
from django.contrib.auth.models import User
from itertools import chain, combinations
from django.http import HttpResponse, JsonResponse
from .models import Feedback
from django.contrib.auth.decorators import login_required
import json

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


def featured_music(request):
    # Define a list of keywords to search for in playlist names
    keywords = [ 'Pop','Rock','K-pop', 'Chinese', 'Japanese','Nepali', 'Bollywood']

    # Fetch playlists for each keyword
    featured_playlists = []
    for keyword in keywords:
        # Fetch a list of featured playlists for the current keyword
        playlists = sp.search(q=keyword, type='playlist', limit=1)

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

def get_all_songs():
    # Fetch a list of featured playlists
    playlists = sp.featured_playlists(limit=1)
    
    # If no playlists were found, return an empty dictionary
    if not playlists['playlists']['items']:
        return {}

    # Randomly select a playlist
    selected_playlist = random.choice(playlists['playlists']['items'])
    playlist_uri = selected_playlist['uri']

    # Fetch tracks from the selected playlist
    tracks_data = sp.playlist_tracks(playlist_uri)["items"]

    # Extract essential details for each track
    all_music = {}
    for track_data in tracks_data:
        track = track_data["track"]
        
        # Get the track's main artist's details
        artist_uri = track["artists"][0]["uri"]
        artist_info = sp.artist(artist_uri)
        album_image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None

        song_key = track["name"]  # Assuming that the name of the song is unique
        all_music[song_key] = {
            "uri": track["uri"],
            "name": track["name"],
            "artist_name": track["artists"][0]["name"],
            "artist_popularity": artist_info["popularity"],
            "artist_genres": artist_info["genres"],
            "album_name": track["album"]["name"],
            "track_popularity": track["popularity"],
            "album_image": album_image_url,
            "preview_url": track.get("preview_url") 
        }

    return all_music

def listening_history(user):
    # Fetch the listening history entries for the user
    user_history_entries = PlayHistory.objects.filter(user=user).order_by('date_played')

    # Create a list to represent the user's listening history with additional details
    user_history = [
        {
            "song_title": entry.song_title,
            "artist_name": entry.artist_name,  # Replace with the actual field name in your model
            "album_image": entry.album_image,  # Replace with the actual field name in your model
        }
        for entry in user_history_entries
    ]

    # Convert the list of dictionaries to a list of tuples
    user_history_tuples = [
        (
            entry["song_title"],
            entry["artist_name"],
            entry["album_image"]
        )
        for entry in user_history
    ]

    # print("listening history", user_history_tuples)
    return user_history_tuples

def get_user_song_data():
    # Fetch all users
    users = User.objects.all()

    # Create a dictionary to store the listening history
    user_song_data = {}

    # Iterate through each user
    for user in users:
        # Fetch the listening history entries for the user
        user_history_entries = PlayHistory.objects.filter(user=user).values_list('song_title', 'artist_name', 'album_image')

        # Convert the queryset of tuples to a set of tuples
        user_history_entries = {tuple(entry) for entry in user_history_entries}

        # Store the listening history in the dictionary
        user_song_data[user.username] = user_history_entries
    # print("songs",user_song_data)
    return user_song_data


def generate_random_recommendations(min_confidence):
    # Generate a list of random songs with high confidence
    all_music = get_all_songs()
    
    random_songs = get_random_songs(all_music)
    random_recommendation = random.sample(random_songs, min(5, len(random_songs)))
    random_recommendations = [{'song': song, 'song_details': all_music[song]} for song in random_recommendation]
    return random_recommendations

def generate_random_matrix(min_confidence):
    # Generate a list of random songs with high confidence
    all_music = get_all_songs()
    random_songs = get_random_songs(all_music)
    random_matrix = random.sample(random_songs, min(5, len(random_songs)))
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

def recommend_songs(song_data, association_rules, user_obj):
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
                song_title, artist_name, album_image = song_tuple

                if artist_name and album_image:
                    recommendations.append({
                        'song': song_title,
                        'confidence': confidence,
                        'song_details': {
                            'artist_name': artist_name,
                            'album_image': album_image,
                        },
                    })

    return recommendations


def recommend_song(request, username):
    user_obj = get_object_or_404(User, username=username)
    min_support_threshold = 0.2
    min_confidence = 0.5

    # Fetch the listening history for the current user
    user_listening_history = listening_history(user_obj)
    song_data = get_user_song_data()
    data = get_user_song_list()
    print("list", data)
    # print("song",song_data)
    frequent_itemsets = generate_frequent_itemsets(song_data, min_support_threshold)
    association_rule = generate_association_rules(frequent_itemsets)
    recommendations = recommend_songs(song_data, association_rule,user_obj)
    random_songs = random.sample(recommendations, min(5, len(recommendations)))
    matrix = recommend(user_obj,data)
    print("matrix",matrix)

    # If there are no recommendations, generate a random playlist
    if not recommendations:
        song = generate_random_recommendations(0.5)
        random_recommendation_matrix = generate_random_matrix(0.5)
        print("song",song)
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
    k = 5
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
    # Pass the processed data to the template
    
    # return render(request, 'collections.html', {'user_song_list': user_song_list, 'recommended_songs': recommended_song_details})



@login_required  # Decorator to ensure the user is authenticated
def submit_feedback(request, username):
    user = get_object_or_404(User, username=username) 
    if request.method == 'POST':
        user = request.user
        preferred_algorithm = request.POST.get('algorithm')

        # Save the feedback to the database
        Feedback.objects.create(user=user, algorithm=preferred_algorithm)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
