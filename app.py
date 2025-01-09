from flask import Flask, render_template, request

app = Flask(__name__)

# Route for handling the home page (and playlist conversion)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_url = request.form.get('playlist_url')
        # Logic to determine whether it's a Spotify or Apple Music URL
        if 'spotify' in playlist_url.lower():
            result = f"Converting Spotify playlist: {playlist_url}"
            # Add Spotify playlist conversion logic here
        elif 'music.apple' in playlist_url.lower():
            result = f"Converting Apple Music playlist: {playlist_url}"
            # Add Apple Music playlist conversion logic here
        else:
            result = "Invalid URL. Please provide a valid Spotify or Apple Music playlist URL."

        return render_template('index.html', result=result)
    
    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(debug=True)
