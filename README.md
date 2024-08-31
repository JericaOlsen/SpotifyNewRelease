# Spotify New Releases Script


## Description

Script that will create a playlist for the user of the newest releases from their followed artists from the past week.
 
## Installation

```bash
pip install spotipy --upgrade
```

Install spotipy to be able to access Spotify's music data. For more information on this library use this site,
[Spotipy Documentation](https://spotipy.readthedocs.io/en/2.24.0/)


## Instructions

### Create an Application

First you need to create an application through the Spotify developers site. You'll need to then create a new project to get your client ID, secret, and redirect URI.

[Spotify Developer Site](https://developer.spotify.com/)

Make sure to set your redirect URI as http://localhost:8080 so that spotipy authorization will work.

### Get Access

Get access to Spotify's data using the authorization flow and import other neccessary modules.

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import date, timedelta
import json


def getAccess(c_id, c_secret, redirect, scope):
    """_summary_

    Args:
        c_id (string): Client ID
        c_secret (string): Client secret
        redirect (string): redirect URI
        scope (string): scope of permissions allowed

    Returns:
        sp: spotify object from user's login 
    """

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=c_id,
    client_secret=c_secret,
    redirect_uri=redirect,
    scope=scope
    ))

    return sp
```

### Get a List of New Songs

Create a list of new song IDs from followed artists. Also create a playlist to later put these songs into.If the playlist already exist it will not be duplicated. GetNewTracks will put all the newest tracks from the past year into the song list on the first run and only get new song from the past week every other run.

```python
def createPlaylist(sp,user):
    """_summary_

    Args:
        sp (Spotify Object): spotify object from user's login 
        user : current user's information

    Returns:
        0 or nothing
    """
    desc = "Newest releases based on your followed artists for this year. This playlist will update 1 week from now"
   
    sp.user_playlist_create(user=user['id'],name='Newest_Releases',public=True,description=desc)
    return 0

def doesPlaylistExist(sp):
    """_summary_

    Args:
        sp (Spotify Object): spotify object from user's login 

    Returns:
        p_exists: Bool showing if the playlist already exists in user's library
    """
    playlist_list = sp.current_user_playlists()

    p_exists = False
    for item in playlist_list['items']:
        if item['name'] == 'Newest_Releases':
            playlist_id = item['id']
            p_exists = True

    return p_exists

def getAllFollowedArtists(sp):
    """_summary_

    Args:
        sp (Spotify Object): spotify object from user's login 

    Returns:
        followed_artist: a list of user's followed artists
    """
    followed_artists = []
    results = sp.current_user_followed_artists()
    followed_artists.extend(results['artists']['items'])

    # Fetch more pages if available
    while results['artists']['next']:
        results = sp.next(results['artists'])
        followed_artists.extend(results['artists']['items'])
    
    return followed_artists

def getNewTracks(sp,user,today,one_week_past):
    """_summary_

    Args:
        sp (Spotify Object): spotify object from user's login 
        user : current user's information
        today (Object): Object that contains today's date
        one_week_past (Object): Object that contains the date of one week from today

    Returns:
        songList: list of song IDs
    """
    results = getAllFollowedArtists(sp)
    newR = []
    first_run = False
    if doesPlaylistExist(sp) == False:
            createPlaylist(sp,user)
            first_run = True
    for item in enumerate(results): #gets the list of followed artists

        results_a = sp.artist_albums(item[1]['uri'], album_type='album')
        albums = results_a['items']

        if first_run == True:
            for a in albums:
                if int(a['release_date'][0:4]) >= today.year: #for the first run
                    newR.append(a)
        else:
            for a in albums:
                if int(a['release_date'][0:4]) >= one_week_past.year and int(a['release_date'][6:7]) >= one_week_past.month and int(a['release_date'][8:9]) >= one_week_past.day: #gets the list of albums released withing a certian date
                    newR.append(a)



    songList = []
    for album in newR:
        tracks = sp.album_tracks(album_id=album['uri'], limit=20)
        for t in tracks['items']:
            songList.append(t['uri'])

    return songList
```

### Add Songs to Playlist

Adds songs into the created playlist and clears songs from previous runs. If there are no new songs from the past week it will keep old songs and edit description to show this.

```python
def addSongs(user,sp, songList, one_week_past):
    """_summary_

    Args:
        sp (Spotify Object): spotify object from user's login 
        user : current user's information
        songList (list): list of song IDs
        one_week_past (Object): Object that contains the date of one week from today

    Returns:
        0
    """

    prePlaylist = sp.user_playlists(user= user['id'])
    for p in prePlaylist['items']:
        if p['name'] == 'Newest_Releases':
            playlist_id = p['id']
            break

    if songList == []:
        new_desc = 'No New Releases from ' + str(one_week_past.month) + '-' + str(one_week_past.day) + '-' + str(one_week_past.year)
        sp.playlist_change_details(playlist_id=playlist_id, description=new_desc)
        return 0


    tracks = sp.playlist_tracks(playlist_id)
    track_ids = [item['track']['id'] for item in tracks['items']]

    # If there are tracks to remove
    if track_ids:
        # Remove all tracks from the playlist
        sp.playlist_remove_all_occurrences_of_items(playlist_id, track_ids)

    playlist = sp.playlist(playlist_id) 
    if playlist['description'] != "Newest releases based on your followed artists for this year. This playlist will update 1 week from now":
        new_desc = 'Newest releases from ' + str(one_week_past.month) + '-' + str(one_week_past.day) + '-' + str(one_week_past.year)
        sp.playlist_change_details(playlist_id=playlist_id, description=new_desc)

    end = 100
    start = 0
    for i in range(0,len(songList)+1,100):
        sp.user_playlist_add_tracks(user=user['id'],playlist_id= playlist_id,tracks=songList[start:end])
        
        end+=100
        if end > len(songList):
            end = len(songList)
        start+=100
    return 0
```
### Main Implementation

Make sure to hide client ID and secret in a separate file so they are not hardcoded into this script.

```python
def main():
    
    today = date.today()
    one_week_past = today - timedelta(weeks=1)

    scope = "user-follow-read playlist-modify-private playlist-modify-public playlist-read-private user-library-read"

    with open('clientInfo.json') as client_file:
        client_info = json.load(client_file)

    CLIENT_ID = client_info['CLIENT_ID']
    CLIENT_SECRET = client_info['CLIENT_SECRET']
    REDIRECT_URI='http://localhost:8080'  # Make sure this matches your redirect URI

    sp = getAccess(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope)
    user = sp.current_user()


    songList = getNewTracks(sp,user,today,one_week_past)

    addSongs(user,sp,songList,one_week_past)
```
## Usage

After correctly implementing the steps above you should have a Newest_Releases playlist in your library

## Automating

To automate this script you can go to your computers task scheduler and create a new task. For the action section put "Start a New Program" and put the path to the script in the "Program/Script" section. Make sure to convert the script.py file into a .exe file so it will execute opening opening. Also make sure to set this task to run when the user is logged on otherwise it will not work.