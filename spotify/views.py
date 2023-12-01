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
    keywords = [ 'Hollywood','K-pop', 'Chinese', 'Japanese','Nepali', 'Bollywood']

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
    playlists = sp.featured_playlists(limit=5)
    
    # If no playlists were found for the keyword, skip to the next one
    if not playlists['playlists']['items']:
        return {}

    # Extract essential details for each playlist
    playlist_data = random.choice(playlists['playlists']['items'])
    playlist_uri = playlist_data['uri']
    playlist_name = playlist_data['name']

        # Fetch all tracks from the selected playlist
    all_tracks_data = sp.playlist_tracks(playlist_uri)["items"]

        # Randomly select 10 tracks from all tracks
    selected_tracks_data = random.sample(all_tracks_data, min(10, len(all_tracks_data)))

        # Extract essential details for each selected track in the playlist
    all_music = []
    for track_data in selected_tracks_data:
        track = track_data["track"]
            
            # Get the track's main artist's details
        artist_uri = track["artists"][0]["uri"]
        artist_info = sp.artist(artist_uri)
        album_image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None

        all_music.append({
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
        all_music.append({
            "playlist_name": playlist_name,
            "tracks": all_music,
        })
        # print('get all song', all_music);
    return all_music


def listening_history(user):
    # Fetch the listening history entries for the user
    user_history_entries = PlayHistory.objects.filter(user=user).order_by('date_played')

    # Create a list to represent the user's listening history
    user_history = [entry.song_title for entry in user_history_entries]

    return user_history


def get_user_song_data():
    # Fetch all users
    users = User.objects.all()

    # Create a dictionary to store the listening history
    user_song_data = {}

    # Iterate through each user
    for user in users:
        # Fetch the listening history entries for the user
        user_history_entries = PlayHistory.objects.filter(user=user).values_list('song_title', flat=True)
        
        # Store the listening history in the dictionary
        user_song_data[user.username] = set(user_history_entries)

    return user_song_data

def generate_listening_history(min_support_threshold):
    # Fetch all users
    users = User.objects.all()

    # Create a list to store the listening history
    listening_history = []

    # Count occurrences of each item (song) in the entire dataset
    item_counts = {}

    # Iterate through each user
    for user in users:
        # Fetch the listening history entries for the user
        user_history_entries = PlayHistory.objects.filter(user=user).order_by('date_played')
        
        # Create a list to represent the user's listening history
        user_history = [entry.song_title for entry in user_history_entries]
        
        # Update item counts based on the current user's history
        for itemset in combinations(user_history, 2):
            item_counts[itemset] = item_counts.get(itemset, 0) + 1

        # Append the user's history to the listening history list
        listening_history.append(frozenset(user_history))  # Convert to frozenset to ensure unique items

    # Calculate support for each itemset
    dataset_size = len(listening_history)
    min_support_count = int(min_support_threshold * dataset_size)  # Convert to int for count comparison
    itemset_support = {frozenset(itemset): count / dataset_size for itemset, count in item_counts.items() if count >= min_support_count}
    
    # Filter itemsets based on the minimum support threshold
    frequent_itemsets = {support: [itemset for itemset, support_value in itemset_support.items() if support_value == support] for support in set(itemset_support.values())}
    
    return frequent_itemsets

def find_consequent_candidates(user_song_data, current_user, antecedent, min_consequent_support=5):
    consequent_candidates = set()

    for user, song_list in user_song_data.items():
        if user != current_user:
            found_antecedent = False

            # Iterate through the user's song list
            for song in song_list:
                if found_antecedent:
                    # Add all songs that come after any song in the antecedent
                    consequent_candidates.add(song)

                # Check if the current song is in the antecedent
                if song in antecedent:
                    found_antecedent = True

            # If the user is not the current user and has a sufficiently long listening history, add all songs from the user's listening history
            if found_antecedent and len(song_list) >= min_consequent_support:
                consequent_candidates.update(song_list)

    return consequent_candidates



def calculate_confidence(user_song_data, antecedent, consequent, min_confidence=0.5):
    antecedent_set = set(antecedent)
    # print(antecedent_set)
    
    # Print all subsets of the antecedent for debugging
    # print("All Antecedent Subsets:")
    # for subset in powerset(antecedent_set):
    #     print(subset)

    antecedent_support = sum(1 for song_list in user_song_data.values() if antecedent_set.issubset(song_list))

    rule_set = antecedent_set.union(consequent)
    rule_support = sum(1 for song_list in user_song_data.values() if rule_set.issubset(song_list))

    confidence = rule_support / antecedent_support if antecedent_support > 0 else 0

    # Debugging print statements
    # print("Antecedent Support:", antecedent_support)
    # print("Rule Support:", rule_support)
    # print("Confidence:", confidence)

    return max(confidence, min_confidence)


def generate_user_association_rules(user_song_data, min_support_threshold, confidence_threshold):
    association_rules = []

    frequent_itemsets = generate_listening_history(min_support_threshold)

    for current_user, antecedentes in user_song_data.items():
        for antecedent in antecedentes:
            # Find consequent songs that co-occur with the antecedent for other users
            consequent_candidates = find_consequent_candidates(user_song_data, current_user, antecedent)

            for consequent in consequent_candidates:
                # Calculate confidence based on the support of antecedent and consequent
                confidence = calculate_confidence(user_song_data, antecedent, consequent)
                # print("confidence",confidence)

                if confidence >= confidence_threshold:
                    association_rules.append({
                        'user': current_user,
                        'antecedent': antecedent,
                        'consequent': consequent,
                        'confidence': confidence
                    })

    return association_rules




def recommend_songs(listening_history, association_rules, all_songs):
    updated_history = {}

    for rule in association_rules:
        user, antecedent, consequent, confidence = rule['user'], rule['antecedent'], rule['consequent'], rule['confidence']
        antecedent_str = str(antecedent)
        consequent_str = str(consequent)

        if antecedent_str in listening_history:
            # Check if consequent_str is in the all_song dictionary
            if consequent_str in all_songs:
                existing_details = updated_history.get(consequent_str, {})
                existing_confidence = existing_details.get('confidence', 0)

                # Compare confidence with the existing value
                if consequent_str not in listening_history or confidence > existing_confidence:
                    song_details = all_songs[consequent_str]

                    # Debugging print statements
                    # print(f"Consequent: {consequent_str}")
                    # print(f"Song Data Keys: {all_songs.keys()}")
                    updated_history[consequent_str] = {
                        'confidence': confidence,
                        'song_details': song_details
                    }

    
    result = [{'song': song, 'confidence': details['confidence'], 'song_details': details['song_details']} for song, details in updated_history.items()]
    
    # Add more print statements for debugging
    # print("Listening History:", listening_history)
    # print("Association Rules:", association_rules)
    # print("Updated History:", updated_history)
    print("Result:", result)

    result.sort(key=lambda x: x['confidence'], reverse=True)
    return result


def recommend_song(request, username):
    user_obj = get_object_or_404(User, username=username)
    min_support_threshold = 0.2
    min_confidence = 0.5

    # Fetch the listening history for the current user
    user_listening_history = listening_history(user_obj)
    
    # If the user's history is empty, generate random recommendations with high confidence
    if not user_listening_history:
        random_recommendations = generate_random_recommendations(min_confidence)

        random_selection = random.sample(random_recommendations, min(10, len(random_recommendations)))
    
        context = {
            'user_obj': user_obj,
            'recommended_songs': random_selection,
        }
    else:
        # Create subsets of two
        unique_antecedentes = list(set(user_listening_history))
        subsets_of_two = list(combinations(unique_antecedentes, 2))

        song_data = get_user_song_data()
        # print("song_data", song_data)
        all_songs = get_all_songs() # <-- Corrected here
        print("all_songs", all_songs)
        
        find_consequent = find_consequent_candidates(song_data, user_obj, user_listening_history)
        confidence = calculate_confidence(song_data, subsets_of_two, find_consequent)

        association_rules = generate_user_association_rules(song_data, min_support_threshold, min_confidence)
        # print("rules", association_rules)

        # Recommend songs based on association rules
        recommended_songs = recommend_songs(user_listening_history, association_rules, all_songs)

        # Randomly select 10 recommendations
        random_recommendations = random.sample(recommended_songs, min(10, len(recommended_songs)))

        # Print the recommendations in the terminal
        print("Recommended Songs:")
        for song in random_recommendations:
            song_name = song['song']
            confidence = song['confidence']
            song_details = song['song_details']

            # Accessing specific details from song_details dictionary
            artist_name = song_details.get('artist_name', 'N/A')
            album_name = song_details.get('album_name', 'N/A')
            album_image = song_details.get('album_image', 'N/A')
            
        print(f"Song: {song_name}, Confidence: {confidence}, Artist: {artist_name}, Album: {album_name}, Album Image: {album_image}")
        context = {
            'user_obj': user_obj,
            'recommended_songs': random_recommendations,
        }

    return render(request, 'collections.html', context)


def generate_random_recommendations(min_confidence):
    # Generate a list of random songs with high confidence
    all_music = get_all_songs()
    # num_recommendations = min(10, len(all_music))  # Limit to 15 songs or the number of available tracks
    random_songs = get_random_songs(10, all_music)
    random_recommendations = [{'song': song, 'confidence': min_confidence * 100} for song in random_songs]
    return random_recommendations

def get_random_songs(num_songs, featured_tracks):
    # Extract song names from the featured tracks
    all_songs = [track['name'] for track in featured_tracks]
    
    # Replace this with your logic to fetch random songs (e.g., from a database or API)
    return random.sample(all_songs, num_songs)
