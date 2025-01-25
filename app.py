from flask import Flask, render_template, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)


SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope="playlist-read-private"))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        token_info = sp.auth_manager.get_access_token(code)
        sp.auth_manager.token = token_info['access_token']
        return "Successfully authenticated with Spotify."
    return "Error: No code received."

def get_spotify_playlist_tracks(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]  # Extract playlist ID
    try:
        playlist = sp.playlist_tracks(playlist_id)
    except Exception as e:
        print(f"Error fetching playlist {playlist_id} tracks: {e}")
        return None
    
    tracks = playlist.get('items', [])
    track_info = []
    for item in tracks:
        track_info.append({
            'name': item['track']['name'],
            'artist': item['track']['artists'][0]['name']
        })
    
    return track_info

def search_apple_music(track_name, artist_name):
    search_query = f"{track_name} {artist_name}".replace(" ", "+")
    url = f"https://music.apple.com/us/search?term={search_query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error with Apple Music request: {e}")
        return None
    
    if app.config.get("DEBUG"):
        print(response.content[:500])  

    soup = BeautifulSoup(response.content, 'html.parser')
    track_link = soup.find('a', {'class': 'click-action'})
    if track_link:
        return f"https://music.apple.com{track_link['href']}"
    return None

def search_spotify(track_name, artist_name):
    query = f"track:{track_name} artist:{artist_name}"
    try:
        results = sp.search(q=query, type='track', limit=1)
    except Exception as e:
        print(f"Error searching Spotify: {e}")
        return None
    
    if results['tracks']['items']:
        return results['tracks']['items'][0]['external_urls']['spotify']
    return None

def get_apple_music_playlist_tracks(playlist_url):
    try:
        response = requests.get(playlist_url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Error with Apple Music request: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    track_elements = soup.find_all('a', {'class': 'songs-list-row__link'})
    tracks = []
    for track_element in track_elements:
        track_name = track_element.find('span', {'class': 'songs-list-row__song-name'}).get_text(strip=True)
        artist_name = track_element.find('span', {'class': 'songs-list-row__artist-name'}).get_text(strip=True)
        tracks.append({'name': track_name, 'artist': artist_name})

    return tracks

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_url = request.form.get('playlist_url')
        result = None

        if 'spotify' in playlist_url.lower():
            start_time = time.time()
            tracks = get_spotify_playlist_tracks(playlist_url)
            if not tracks:
                result = "Error fetching Spotify tracks."
            else:
                apple_music_links = []
                for track in tracks:
                    link = search_apple_music(track['name'], track['artist'])
                    if link:
                        apple_music_links.append(link)

                if apple_music_links:
                    result = "Apple Music Links:<br>" + "<br>".join(apple_music_links)
                else:
                    result = "No matching tracks found on Apple Music."
            print(f"Spotify processing time: {time.time() - start_time} seconds")

        elif 'music.apple' in playlist_url.lower():
            start_time = time.time()
            tracks = get_apple_music_playlist_tracks(playlist_url)
            if not tracks:
                result = "Error fetching Apple Music tracks."
            else:
                spotify_links = []
                for track in tracks:
                    link = search_spotify(track['name'], track['artist'])
                    if link:
                        spotify_links.append(link)

                if spotify_links:
                    result = "Spotify Links:<br>" + "<br>".join(spotify_links)
                else:
                    result = "No matching tracks found on Spotify."
            print(f"Apple Music processing time: {time.time() - start_time} seconds")

        else:
            result = "Invalid URL. Please provide a valid Spotify or Apple Music playlist URL."

        return render_template('index.html', result=result)

    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(debug=True)
