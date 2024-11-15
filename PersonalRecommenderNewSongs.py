import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Laad de .env bestand
load_dotenv('Acodes.env')

# Haal de CLIENT_ID en CLIENT_SECRET op
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

print(client_id)
print(client_secret)
print("hello world")

# Definieer de scopes die je wilt gebruiken
scope = "user-library-read user-top-read playlist-read-private playlist-modify-public"

# Initialiseer de Spotify OAuth2
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:8888/callback",
                                               scope=scope))

# Print de URL voor gebruikers om in te loggen
auth_url = sp.auth_manager.get_authorize_url()
print("Ga naar de volgende URL om in te loggen:", auth_url)

# Wacht op redirect en pak de token
token_info = sp.auth_manager.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token_info)

# Gebruik Spotipy zoals eerder
user = sp.current_user()
print(f'Ingelogd als: {user["display_name"]}')


# Haal de nummers op die de gebruiker heeft geliked
liked_tracks = sp.current_user_saved_tracks(limit=50)
liked_track_ids = {item['track']['id'] for item in liked_tracks['items']}

# Haal de tracks uit de afspeellijsten van de gebruiker op
playlists = sp.current_user_playlists()
playlist_track_ids = set()
for playlist in playlists['items']:
    tracks = sp.playlist_tracks(playlist['id'])
    for item in tracks['items']:
        playlist_track_ids.add(item['track']['id'])

# Combineer de gelikete nummers en de tracks uit de afspeellijsten
user_track_ids = liked_track_ids.union(playlist_track_ids)

# Haal de top tracks van de gebruiker op
top_tracks = sp.current_user_top_tracks(limit=50)

# Haal gerelateerde tracks van een geselecteerd nummer op
seed_track_id = 'NUMMER_ID'  # Vul hier het ID van het geselecteerde nummer in
related_tracks = sp.recommendations(seed_tracks=[seed_track_id], limit=50)

# Filter de tracks die de gebruiker al heeft geliked of in een playlist heeft gezet
unique_tracks = {track['id']: track for track in related_tracks['tracks'] if track['id'] not in user_track_ids}

# Maak een nieuwe playlist met de gefilterde tracks
user_id = sp.me()['id']
playlist = sp.user_playlist_create(user_id, 'Gepersonaliseerde Aanbevelingen')
sp.playlist_add_items(playlist['id'], list(unique_tracks.keys()))