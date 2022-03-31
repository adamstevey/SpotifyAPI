from flask import Flask, request, url_for, session, redirect
from pygame import CONTROLLER_BUTTON_DPAD_RIGHT
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

app = Flask(__name__)

app.secret_key = "OKHjhdkjshdkjsh"
app.config["SESSION_COOKIE_NAME"] = "Adams Cookie"
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/redirect")
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    all_songs = []
    iter = 0

    # GRAB JSON DATA FOR ALL SAVED SONGS
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=iter*50)['items']
        iter += 1
        all_songs+=items
        if (len(items) < 50):
            break  
    
    # GET TITLE OF EVERY SONG FROM JSON
    titles = [song['track']['name'] for song in all_songs]

    # PRINT IN HTML
    return str(titles)

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info["expires_at"] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    return token_info

# APP CLIENT ID
CLIENT_ID="77aba330be404a389dcfa8229e53d203"

# APP CLIENT SECRET
CLIENT_SECRET="a827686bd3f042f89af3f56fcc1e4c82"
SCOPE = "user-library-read"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope=SCOPE
    )


