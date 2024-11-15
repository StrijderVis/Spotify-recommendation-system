import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Authenticatie
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="YOUR_REDIRECT_URI",
                                               scope="user-top-read playlist-modify-public"))

# Haal top tracks van de gebruiker op
top_tracks = sp.current_user_top_tracks(limit=50)

# Haal gerelateerde tracks van een geselecteerd nummer op
seed_track_id = 'NUMMER_ID'  # Vul hier het ID van het geselecteerde nummer in
related_tracks = sp.recommendations(seed_tracks=[seed_track_id], limit=50)

# Combineer de tracks en verwijder duplicaten
all_tracks = {track['id']: track for track in top_tracks['items']}
for track in related_tracks['tracks']:
    all_tracks[track['id']] = track

# Maak een nieuwe playlist met de gecombineerde tracks
user_id = sp.me()['id']
playlist = sp.user_playlist_create(user_id, 'Gepersonaliseerde Aanbevelingen')
sp.playlist_add_items(playlist['id'], list(all_tracks.keys()))
