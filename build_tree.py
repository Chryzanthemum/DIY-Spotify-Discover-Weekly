# This script generates a list of song ids, pulls the features for each song id, then builds the annoy index
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from annoy import AnnoyIndex
from utils import recurse_playlist, get_features, get_metadata

def build_annoy_index(array, trees=10):
    # vector size is feature length, idk wtf angular does
    t = AnnoyIndex(11, 'angular')
    for i in range(len(array)):
        t.add_item(i, array[i])
    # once this is built, you can't add items to it. Should we build it somewhere else?
    t.build(trees)
    
    return t

# ENV VARIABLE
cid = st.secrets["cid"]
secret = st.secrets["secret"]
username = 'Ben'
credentials = SpotifyClientCredentials(
        client_id=cid,
        client_secret=secret)
sp = spotipy.Spotify(auth_manager=credentials)


# TODO - read from not this lmao
# everything from here to the id feature request should probably be a different file that has multiple ways of generating song ids
user_ids = [
    'kirstendodo',
    '1260745480',
    '1255526461',
    'athenajiang',
    '1239664093',
    '1268639225',
    '22eja5lr4xyqrmdgb4jox74pi',
    'russellkim98',
    '1213055384',
    '12563360',
    '1218288200',
    '22vxpm5y7bws42rgecwwdtqzq',
    '2lb6yucjb2mmlbpqvv7f6tpa',
    'hahowie',
    '1233302457',
    'clairehuangg',
    'gmfrlife',
    'karawho',
    '1210134132',
    'gracehuang22',
    'sangeethaisrofl',
    '124028238',
    '1228739853',
    '1249053478',
    '1249402231',
    '1261634901',
    'jasonliao',
    '12101413836',
    '227lrr7ufyoef3thjhnzjcbhi',
    '1263186670',
    '126549512',
    '22tbkcbk3npj7dmozb5xcvegq',
    '1258256267',
    'zenbhang',
    '1249768840',
    '1251291991',
    '1293249673',
    '12184871363',
    '1225107231',
    '21jm5sg2qelg57la434krzpjy',
    '22n5d3jkyzx6ucmdh6stknedi'
]

playlist_ids = set()
for ui in user_ids:
    try:
        r = sp.user_playlists(ui, limit=50)
        for i in r['items']:
            playlist_ids.add(i['id'])
    except:
        print(ui, 'error')

all_playlists = list()
for i in playlist_ids:
    all_playlists.extend(recurse_playlist(sp, list(), str.replace(i, 'https://open.spotify.com/playlist/', '')))


ids = set()
for p in all_playlists:  
    if 'tracks' in p:
        for item in p['tracks']['items']:
            try:
                if item['track']['id'] is not None:
                    ids.add(item['track']['id'])
            except:
                pass
    elif 'items' in p:
        for item in p['items']:
            try:
                if item['track']['id'] is not None:
                    ids.add(item['track']['id'])
            except:
                pass

# we only expect them to be a set during the data gathering process - after this point, no more modding the list
ids = list(ids)
df_metadata = get_metadata(sp, ids)
df_features = get_features(sp, ids)
# index can just be the integer : song id mapping LMFAO
# if we were big boy MLE we'd keep the feature list in a yaml file somewhere but 
features = np.array(df_features[['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']])
index = build_annoy_index(features)

# I'm not really sure what's the intermediate step between building dev/staging/prod and just running in a notebook
index.save('data/index.ann')
df_features.to_csv('data/features.csv')
df_metadata.to_csv('data/metadata.csv')