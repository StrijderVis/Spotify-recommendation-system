import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Laad het .env bestand
load_dotenv('Acodes.env')

# Haal de CLIENT_ID en CLIENT_SECRET op uit het .env bestand
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
scope = "user-library-read user-top-read playlist-read-private playlist-modify-public"

# Initialiseer de Spotify OAuth2
sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)

# Functie om de gebruiker naar de inlogpagina te leiden
def login():
    auth_url = sp_oauth.get_authorize_url()
    st.markdown(f"<a href='{auth_url}' target='_blank'>Klik hier om in te loggen bij Spotify</a>", unsafe_allow_html=True)

# Toon een knop die de gebruiker naar de inlogpagina leidt
if "code" not in st.query_params:
    if st.button("Login met Spotify"):
        login()

# Wacht op redirect en pak de token
if "code" in st.query_params:
    code = st.query_params["code"]
    sp_oauth.get_access_token(code)
    token_info = sp_oauth.get_cached_token()
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Gebruik Spotipy zoals eerder
    user = sp.current_user()
    st.write(f"Ingelogd als: {user['display_name']}")

    # Haal de nummers op die de gebruiker heeft geliked
    liked_tracks = sp.current_user_saved_tracks(limit=50)
    liked_track_ids = [item['track']['id'] for item in liked_tracks['items']]
    liked_track_names = [item['track']['name'] for item in liked_tracks['items']]
    top_liked_track_names = liked_track_names[:10]  # Toon alleen de eerste 10

    st.write("Top 10 gelikede nummers:")
    include_liked = st.checkbox("Neem gelikede nummers mee in aanbevelingen", value=True)
    st.write(top_liked_track_names)

    # Haal de top tracks van de gebruiker op
    top_tracks = sp.current_user_top_tracks(limit=50)
    top_track_ids = [item['id'] for item in top_tracks['items']]
    top_track_names = [item['name'] for item in top_tracks['items']]
    top_top_track_names = top_track_names[:10]  # Toon alleen de eerste 10

    st.write("Top 10 nummers:")
    include_top = st.checkbox("Neem top nummers mee in aanbevelingen", value=True)
    st.write(top_top_track_names)

    # Gebruik alleen maximaal 5 seed_tracks op basis van de checkboxes
    seed_tracks = []
    if include_liked:
        seed_tracks.extend(liked_track_ids[:5])
    if include_top:
        seed_tracks.extend(top_track_ids[:5])

    # Beperk het aantal seed_tracks tot maximaal 5 zoals vereist door de Spotify API
    seed_tracks = seed_tracks[:5]

    if seed_tracks:
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=10)
        recommended_track_names = [item['name'] for item in recommendations['tracks']]
        st.write("Aanbevolen nummers:", recommended_track_names)
    else:
        st.write("Geen nummers geselecteerd voor aanbevelingen.")
else:
    st.write("Wacht op gebruikerscode...")
