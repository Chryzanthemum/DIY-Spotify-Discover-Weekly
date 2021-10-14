import pandas as pd


# these should probably all be in a class and use one sp connection but w/e
def recurse_playlist(sp, playlists, id):
    r = sp.playlist(id)
    playlists.append(r)
    if 'tracks' in r:
        if 'next' in r['tracks']:
            if r['tracks']['next'] is not None:
                recurse_playlist(sp, playlists, str.replace(r['tracks']['next'], 'https://api.spotify.com/v1/playlists/', ''))
    elif 'next' in r:
        if r['next'] is not None:
            recurse_playlist(sp, playlists, str.replace(r['next'], 'https://api.spotify.com/v1/playlists/', ''))
    else:
        pass

    return playlists

def get_metadata(sp, ids):
    metadata = list()
    # 50 limit on api call    
    for i in range(0,len(ids),50):
        meta = sp.tracks(ids[i:i+50])
        for data in meta['tracks']:
            artists = list()
            if data is not None:
                for artist in data['artists']:
                    artists.append(artist['id'])
                metadata.append({"song_id":data['id'],  
                                 "artists":artists, 
                                 "song_name":data['name'], 
                                 "album_id":data['album']['id'],
                                 "album_name":data['album']['name'],
                                 "popularity":data['popularity']})
    return pd.DataFrame(metadata)

def get_features(sp, ids):
    features = []
    # 50 limit on api call
    for i in range(0,len(ids),50):
        audio_features = sp.audio_features(ids[i:i+50])
        for track in audio_features:
            if track is not None:
                features.append(track)
    
    return pd.DataFrame(features)
