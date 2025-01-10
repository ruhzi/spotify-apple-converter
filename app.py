from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup

# Initialize Flask app
app = Flask(__name__)

# Spotify API credentials (replace these with your own)
SPOTIPY_CLIENT_ID = '8bb9dd40e75f43dd9b34b3ce3d1ef581'
SPOTIPY_CLIENT_SECRET = '3dbd6db0309e4350aa4461088cfa75bf'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

# Set up Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope="playlist-read-private"))

@app.route('/callback')
def callback():
    # Get the authorization code from the request
    code = request.args.get('code')

    if code:
        # Get the access token using the code
        token_info = sp.auth_manager.get_access_token(code)
        
        # Update the 'auth_manager' directly, not reassigning 'sp'
        sp.auth_manager.token = token_info['access_token']

        # Now you can use 'sp' to make Spotify API requests
        return "Successfully authenticated with Spotify."

    return "Error: No code received."

# Function to fetch playlist tracks from Spotify
def get_spotify_playlist_tracks(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]  # Extract playlist ID
    playlist = sp.playlist_tracks(playlist_id)
    tracks = playlist['items']
    
    track_info = []
    for item in tracks:
        track_info.append({
            'name': item['track']['name'],
            'artist': item['track']['artists'][0]['name']
        })
    
    return track_info

# Function to search Apple Music for a track
def search_apple_music(track_name, artist_name):
    search_query = f"{track_name} {artist_name}".replace(" ", "+")
    url = f"https://music.apple.com/us/search?term={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first track link
    track_link = soup.find('a', {'class': 'songs-list-row__link'})
    if track_link:
        return f"https://music.apple.com{track_link['href']}"
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_url = request.form.get('playlist_url')
        result = None

        if 'spotify' in playlist_url.lower():
            tracks = get_spotify_playlist_tracks(playlist_url)
            apple_music_links = []
            for track in tracks:
                link = search_apple_music(track['name'], track['artist'])
                if link:
                    apple_music_links.append(link)

            if apple_music_links:
                result = "Apple Music Links:<br>" + "<br>".join(apple_music_links)
            else:
                result = "No matching tracks found on Apple Music."
        
        elif 'music.apple' in playlist_url.lower():
            result = "Apple Music integration for Spotify playlist creation is coming soon."

        else:
            result = "Invalid URL. Please provide a valid Spotify or Apple Music playlist URL."

        return render_template('index.html', result=result)

    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(debug=True)
