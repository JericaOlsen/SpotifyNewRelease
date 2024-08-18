import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-follow-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = 'ba81ea4c346b453fa98aa6104ce71fcb', client_secret= '912c87aa34ff4a2292abc1b8275310be', redirect_uri= 'http://localhost/',scope=scope))

user = sp.current_user()
results = sp.current_user_followed_artistsimport spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-follow-read playlist-modify-private playlist-modify-public playlist-read-private user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = 'ba81ea4c346b453fa98aa6104ce71fcb', client_secret= '912c87aa34ff4a2292abc1b8275310be', redirect_uri= 'http://localhost/',scope=scope))

user = sp.current_user()
results = sp.current_user_followed_artists()
newR = []
for item in enumerate(results['artists']['items']): #gets the list of followed artists

    results = sp.artist_albums(item[1]['uri'], album_type='album')
    albums = results['items']
    
    for a in albums:
        if a['release_date'][0:4] == '2024': #gets the list of albums released withing a certian date
            newR.append(a)


songList = []
for album in newR:
    tracks = sp.album_tracks(album_id=album['uri'], limit=20)
    for t in tracks['items']:
        songList.append(t['uri'])
sp.user_playlist_create(user=user['id'],name='Newest_Releases',public=True,description='newest_releases')

prePlaylist = sp.user_playlists(user= user['id'])
playlist_id = prePlaylist['items'][0]['id']

sp.playlist_add_items(playlist_id= playlist_id,items=songList[0])()
for item in enumerate(results['items']):
    print(item)
