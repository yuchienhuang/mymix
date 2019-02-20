import numpy as np
import os
import json


# Spotify API wrapper, documentation here: http://spotipy.readthedocs.io/en/latest/
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials



# Authenticate with Spotify using the Client Credentials flow
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials('d6967ce2057448d4aab3ad9898119c97',  'ad7f82cc26a64f1595b6b3c4cd917243')
#client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(process.env.SPOTIPY_CLIENT_ID,  process.env.SPOTIPY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



def search_tracks(query):
    """
    This demo function will allow the user to search a song title and pick the song from a list in order to fetch
    the audio features/analysis of it
    :param spotify: An basic-authenticated spotipy client
    """
    
    selected_track = None

    search_term = query

        
    results = spotify.search(search_term)
    tracks = results.get('tracks', {}).get('items', [])
    return tracks

    


def get_audio_features( tracks, tracks_artistnames):
    """
    Given a list of tracks, get and print the audio features for those tracks!
    :param spotify: An authenticated Spotipy instance
    :param tracks: A list of track dictionaries
    """
    if not tracks:
        print('No tracks provided.')
        return

    
    track_map = {track.get('id'): track for track in tracks}

    # Request the audio features for the chosen tracks (limited to 50)
    
    tracks_features_response = spotify.audio_features(tracks=track_map.keys())

    desired_features = [
    'tempo',
    'time_signature',
    'key',
    'mode',
    'loudness',
    'energy',
    'danceability',
    'acousticness',
    'instrumentalness',
    'liveness',
    'speechiness',
    'valence'
    ]

    tracks_features_list = []
    for track_features in tracks_features_response:
        
        features_dict = dict()
        for feature in desired_features:
            
            feature_value = track_features.get(feature)

            
            if feature == 'key':
                feature_value = translate_key_to_pitch(feature_value)
            
            features_dict[feature] = feature_value
    
        tracks_features_list.append(features_dict)



    tracks_features_map = {f.get('id'): [tracks_artistnames[i], tracks_features_list[i], "https://open.spotify.com/track/" + f.get('id')] for i, f in enumerate(tracks_features_response)}

    
    
    
    
    

    return tracks_features_map



def translate_key_to_pitch(key):
    """
    Given a Key value in Pitch Class Notation, map the key to its actual pitch string
    https://en.wikipedia.org/wiki/Pitch_class
    :param key: The integer key
    :return: The translated Pitch Class string
    """
    pitches = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
    return pitches[key]