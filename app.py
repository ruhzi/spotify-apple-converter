from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

# Route to handle the homepage and playlist conversion
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_url = request.form.get('playlist_url')
        result = None

        if 'spotify' in playlist_url.lower():
            tracks = get_spotify_playlist_tracks(playlist_url)
            result = f"Tracks from Spotify playlist: {tracks}"
        
        elif 'music.apple' in playlist_url.lower():
            result = "Apple Music integration is coming soon."

        else:
            result = "Invalid URL. Please provide a valid Spotify or Apple Music playlist URL."

        return render_template('index.html', result=result)

    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(debug=True)
