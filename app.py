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

# Titel en logo
st.markdown(""" 
# <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/768px-Spotify_logo_without_text.svg.png" alt="Logo" style="width:100px;"> Song Explorer voor Spotify 
""", unsafe_allow_html=True)

st.text("")
st.text("")

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
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Gebruik Spotipy zoals eerder
    user = sp.current_user()
    st.write(f"Ingelogd als: {user['display_name']}")
    st.text("")
    st.divider()
    st.header("Filters:")

    # Haal de nummers op die de gebruiker heeft geliked
    liked_tracks = sp.current_user_saved_tracks(limit=50)
    liked_track_details = [(item['track']['name'], item['track']['artists'][0]['name'], item['track']['id']) for item in liked_tracks['items'] if 'track' in item and 'id' in item['track']]
    top_liked_track_details = liked_track_details[:10]  # Toon alleen de eerste 10

    include_liked = st.checkbox("Neem gelikete nummers mee in aanbevelingen", value=True)
    with st.expander("Top 10 gelikete nummers"):
        for track, artist, _id in top_liked_track_details:
            st.write(f"{track} - {artist}")
    st.text(" ")

    # Haal de top tracks van de gebruiker op
    top_tracks = sp.current_user_top_tracks(limit=50)
    top_track_details = [(item['name'], item['artists'][0]['name'], item['id']) for item in top_tracks['items'] if 'id' in item]
    top_top_track_details = top_track_details[:10]  # Toon alleen de eerste 10
    
    include_top = st.checkbox("Neem de top geluisterde nummers mee in aanbevelingen", value=True)
    with st.expander("Top 10 geluisterde nummers"):
        for track, artist, _id in top_top_track_details:
            st.write(f"{track} - {artist}")
    st.text(" ")

    # Invoer voor een nummer in
    st.subheader("Voeg een nummer toe om aanbevelingen te genereren:")
    st.caption("(laat leeg als je geen nummer filtering wilt)")
    track_name = st.text_input("Track naam (+ artiest)(optioneel)")

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
    st.divider()

    # Stel de weging van elke soort in.
    seed_tracks = []
    if include_liked:
        seed_tracks.extend([_id for _, _, _id in top_liked_track_details][:1])
    if include_top:
        seed_tracks.extend([_id for _, _, _id in top_top_track_details][:1])
    if search_track_id:
        seed_tracks.extend([search_track_id] * 10)

    # Beperk het aantal seed_tracks tot maximaal 5, anders gaat de spotify API boos doen >:(
    seed_tracks = seed_tracks[:5]

    ## AANBEVOLEN NUMMERS STUK
    st.header("Aanbevolen nummers:")

    # Slider zodat de gebruiker zelf kan instellen hoeveel aanbevolen nummers ze willen
    songamount = st.slider("Aantal aanbevolen nummers", min_value=10, max_value=100, step=10)
    st.write("")
    st.write("")

    # Maak de aanbevelingen
    st.subheader("Aanbevolen nummers:")
    if seed_tracks:
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=songamount)
        recommended_track_details = [(item['name'], item['artists'][0]['name'], item['id']) for item in recommendations['tracks']]
        with st.expander("Aanbevolen nummers"):
            for track, artist, _id in recommended_track_details:
                st.write(f"{track} - {artist}")
        st.write("")
        
        st.subheader("Voeg de aanbevelingen toe aan een spotify playlist:")

        # Invoer voor de naam van de playlist
        playlist_name_input = st.text_input("Naam van de afspeellijst:", f"{track_name} aanbevelingen")

        # Functie om een afspeellijst aan te maken met de playlist naam hiervoor ingevoerd en nummers toe te voegen
        def create_playlist(playlist_name):
            if not playlist_name:
                playlist_name = f"{track_name} aanbevelingen"
            playlist = sp.user_playlist_create(user=user['id'], name=playlist_name)
            sp.user_playlist_add_tracks(user=user['id'], playlist_id=playlist['id'], tracks=[_id for _, _, _id in recommended_track_details])
            st.write(f"Afspeellijst '{playlist_name}' aangemaakt en nummers toegevoegd!")
        
        # Knop om de afspeellijst aan te maken
        if st.button("Maak afspeellijst"):
            create_playlist(playlist_name_input)
    else:
        st.write("Geen nummers geselecteerd voor aanbevelingen.")   
else:
    st.write("Wacht op gebruikerscode...")
