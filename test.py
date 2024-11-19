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
    liked_track_details = [(item['track']['name'], item['track']['artists'][0]['name'], item['track']['id']) for item in liked_tracks['items'] if 'track' in item and 'id' in item['track']]
    top_liked_track_details = liked_track_details[:10]  # Toon alleen de eerste 10

    with st.expander("Top 10 gelikede nummers"):
        include_liked = st.checkbox("Neem gelikede nummers mee in aanbevelingen", value=True)
        for track, artist, _id in top_liked_track_details:
            st.write(f"{track} - {artist}")

    # Haal de top tracks van de gebruiker op
    top_tracks = sp.current_user_top_tracks(limit=50)
    top_track_details = [(item['name'], item['artists'][0]['name'], item['id']) for item in top_tracks['items'] if 'id' in item]
    top_top_track_details = top_track_details[:10]  # Toon alleen de eerste 10

    with st.expander("Top 10 nummers"):
        include_top = st.checkbox("Neem top nummers mee in aanbevelingen", value=True)
        for track, artist, _id in top_top_track_details:
            st.write(f"{track} - {artist}")

    # Invoer voor een nummer en artiest
    st.write("Voeg een nummer en artiest toe om aanbevelingen te genereren:")
    track_name = st.text_input("Track naam")
    artist_name = ""

    # Zoek naar het ingevoerde nummer en vul de artiest automatisch in
    if track_name:
        results = sp.search(q=f"track:{track_name}", type="track", limit=1)
        if results['tracks']['items']:
            search_track_id = results['tracks']['items'][0]['id']
            artist_name = results['tracks']['items'][0]['artists'][0]['name']
            st.write(f"Gevonden nummer: {results['tracks']['items'][0]['name']} - {artist_name}")
        else:
            st.write("Geen nummer gevonden met de opgegeven details.")
            search_track_id = None
    else:
        search_track_id = None

    # Toon de artiest naam automatisch in een niet-bewerkbaar tekstveld
    st.text_input("Artiest naam", artist_name, disabled=True)

    # Gebruik alleen maximaal 5 seed_tracks op basis van de checkboxes en het zoeknummer
    seed_tracks = []
    if include_liked:
        seed_tracks.extend([_id for _, _, _id in top_liked_track_details][:2])
    if include_top:
        seed_tracks.extend([_id for _, _, _id in top_top_track_details][:2])
    if search_track_id:
        # Voeg het input nummer toe voor zwaardere weging
        seed_tracks.append(search_track_id)  # Voeg eenmaal toe voor zwaardere weging

    # Beperk het aantal seed_tracks tot maximaal 5 zoals vereist door de Spotify API
    seed_tracks = seed_tracks[:5]

    if seed_tracks:
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=10)
        recommended_track_details = [(item['name'], item['artists'][0]['name'], item['id']) for item in recommendations['tracks']]
        st.write("Aanbevolen nummers:")
        for track, artist, _id in recommended_track_details:
            st.write(f"{track} - {artist}")
    else:
        st.write("Geen nummers geselecteerd voor aanbevelingen.")
else:
    st.write("Wacht op gebruikerscode...")