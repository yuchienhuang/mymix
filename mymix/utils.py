import numpy as np
import os
import json
#from mymix import display_utils,azlyrics

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
    #keep_searching = True
    selected_track = None

    # Initialize Spotipy
    #spotify = authenticate_client()

    # We want to make sure the search is correct
    # while keep_searching:
    search_term = query

        # Search spotify
    results = spotify.search(search_term)
    tracks = results.get('tracks', {}).get('items', [])
    return tracks

        # if len(tracks) == 0:
        #     print_header('No results found for "{}"'.format(search_term))
        # else:
        #     # Print the tracks
        #     print_header('Search results for "{}"'.format(search_term))
        #     for i, track in enumerate(tracks):
        #         print('  {}) {}'.format(i + 1, track_string(track)))

        # Prompt the user for a track number, "s", or "c"
        # track_choice = input('\nChoose a track #, "s" to search again, or "c" to cancel: ')
        # try:
        #     # Convert the input into an int and set the selected track
        #     track_index = int(track_choice) - 1
        #     selected_track = tracks[track_index]
        #     keep_searching = False
        # except (ValueError, IndexError):
        #     # We didn't get a number.  If the user didn't say 'retry', then exit.
        #     if track_choice != 's':
        #         # Either invalid input or cancel
        #         if track_choice != 'c':
        #             print('Error: Invalid input.')
        #         keep_searching = False

    # Quit if we don't have a selected track
    # if selected_track is None:
    #     return

    # Request the features for this track from the spotify API
    # get_audio_features(spotify, [selected_track])

    # return [selected_track]


# def get_audio_lyrics(tracks):
#     track_artists = [track_string(track).split('-') for track in tracks]

#     print([get_lyrics(track_artist[-1],track_artist[0]) for track_artist in track_artists])

#     return json.dumps([get_lyrics(track_artist[-1],track_artist[0]) for track_artist in track_artists])


def get_audio_features( tracks, tracks_artistnames):
    """
    Given a list of tracks, get and print the audio features for those tracks!
    :param spotify: An authenticated Spotipy instance
    :param tracks: A list of track dictionaries
    """
    if not tracks:
        print('No tracks provided.')
        return

    # Build a map of id->track so we can get the full track info later
    track_map = {track.get('id'): track for track in tracks}

    # Request the audio features for the chosen tracks (limited to 50)
    #print_header('Getting Audio Features...')
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

    
    # Iterate through the features and print the track and info
    # if pretty_print:
    #     for track_id, track_features in track_features_map.items():
    #         # Print out the track info and audio features
    #         track = track_map.get(track_id)
    #         print_audio_features_for_track(track, track_features)

    
    
    

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