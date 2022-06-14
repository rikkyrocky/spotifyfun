from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
app = Flask(__name__)
# note here that '__name__' here refers to the name of this file!
'''Go back from november 2015 to Present and find the average popularity and proportion of explicit 
songs per playlist'''
CLIENT_ID = 'd3f13b4d0b9446fdba2596a68d7ae472'
CLIENT_SECRET = '8f0db90b04ec4fbdae480363392d5bed'
TOKEN_INFO = 'token_info'
SITE_URL = 'http://127.0.0.1:5000'
app.secret_key = "secretkey1234"
app.config['SESSION_COOKIE_NAME'] = "Rick's Cookie"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for('redirectpage', _external=True),
        scope="user-library-read")
#the url_for function allows you to use the path without hardcoding the site
#will work for both localhost:5000/redirect and www.spotifyfun.com/redirect
# also dont save the output of the spotifyOauth function in a variable

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if token_info == None:
        raise "exception"
    else:
        now = int(time.time())
        is_expired = token_info['expires_at'] - now < 60
        if is_expired:
            sp_oauth = create_spotify_oauth()
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        return token_info


@app.route('/')
# this is a decorator, it modifies another function, like the one below
def index():
    return render_template("greet.html", SITE_URL=(SITE_URL + '/login'))

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
    #return render_template('greet.html')
    # redirects user to Spotify login page

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print('user not logged in')
        return redirect(SITE_URL + '/')
    songs = []
    playlists = []
    sp = spotipy.Spotify(auth=token_info['access_token'])
    for item in sp.current_user_saved_tracks(limit=50, offset=50)['items']:
        songs.append(item['track']['name'])
    for item in sp.current_user_playlists(limit=50, offset=0)['items']:
        playlists.append(item['name'])
    print(songs)
    return sp.current_user_saved_tracks(limit=50, offset=0)['items'][0]['track']['name']
    #return str(playlists)
    #return render_template('greet.html')

@app.route('/redirectpage')
def redirectpage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    print(code)
    return redirect(SITE_URL + '/getTracks')

if __name__ == "__main__":
    app.run(debug=True) #lol