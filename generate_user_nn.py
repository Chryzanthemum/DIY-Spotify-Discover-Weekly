import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from annoy import AnnoyIndex
from utils import get_features
from datetime import datetime


def create_playlist(songs):
    user_id = sp.me()['id']
    timestampStr = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    sp.user_playlist_create(user_id, f'Customized Discover Weekly - {timestampStr}')
    print("playlist created!")
    # We don't get the playlist id when we create it, so we take the user's first 50 playlists, then find the name we gave it
    playlists = sp.user_playlists(sp.me()['id'])['items']
    playlist_names = {}
    for i in playlists:
        playlist_names[i['name']] = i['id']
    try:
        playlist_id = playlist_names[f'Customized Discover Weekly - {timestampStr}']
    except:
        print("error! playlist not found")
    sp.playlist_add_items(playlist_id, songs)
    print("songs added to playlist!")

def recurse_saved_songs(sp, songs, offset=0):
    r = sp.current_user_saved_tracks(20, offset)
    for i in r['items']:
        songs.append({"id":i['track']['id'], "added_at":i['added_at']})
    if r['next']:
        offset+=20
        recurse_saved_songs(sp, songs, offset)
    return songs

def get_nn(t, sp, songs):
    nearest_neighbors = list()
    song_features = np.array(get_features(sp, songs)[['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']])
    for s in song_features:
        nearest_neighbors.append(t.get_nns_by_vector(s, 5, search_k=-1, include_distances=True))
        
    df_nearest_neighbors_indices = pd.DataFrame()
    for nn in nearest_neighbors:
        # unpacks tuple and appends to df
        df_nearest_neighbors_indices = df_nearest_neighbors_indices.append(
            pd.DataFrame.from_dict(dict(zip(nn[0], nn[1])), 
                                   orient='index'))
    df_nearest_neighbors_indices = (
        df_nearest_neighbors_indices
        .reset_index()
        .groupby('index', as_index=False)
        .min()
        .rename(columns={"index":"song_index", 0:"distance"})
    )    
    # for each song in songs, we get a few close songs. Return all of them?
    return df_nearest_neighbors_indices

def apply_filtering_criteria(songs_df):
    # stick a bunch of rules on there to get us to 30 songs
    # right now let's just take top 30
    return songs_df.sort_values(by='distance', ascending=False).head(30)[['song_index']]
    
# ENV - VARIABLES
scope = ['user-library-read', "playlist-modify-public"]
cid ='0deb154cdea34cfa9c50fc76938403b9'
secret = '6aa3c3ee390d4421bdc6a860cf33c686'
index = AnnoyIndex(11, 'angular')
index.load('data/index.ann')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = cid,
                                               client_secret = secret,
                                               redirect_uri= 'http://127.0.0.1:5000/spotify/callback',
                                               scope=scope,
                                              open_browser=True))

# Okay, right now this doesn't have to be a df instead of a list, but I promise there will be some use case for this
df_your_songs = pd.DataFrame(recurse_saved_songs(sp, list()))
df_nearest_neighbors_indices = get_nn(index, sp, df_your_songs.head()['id'])
df_filtered_indices = apply_filtering_criteria(df_nearest_neighbors_indices)
df_metadata = pd.read_csv('data/metadata.csv').iloc[list(df_filtered_indices['song_index']), :]

for name in df_metadata['song_name']:
    print(name)
songs = list(df_metadata['song_id'])