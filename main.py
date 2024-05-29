import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-follow-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = 'ba81ea4c346b453fa98aa6104ce71fcb', client_secret= '912c87aa34ff4a2292abc1b8275310be', redirect_uri= 'http://localhost/',scope=scope))

user = sp.current_user()
results = sp.current_user_followed_artists()
for item in enumerate(results['items']):
    print(item)