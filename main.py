import os
import plistlib
import yt_dlp
import requests
from rich import print

def parse_favorite_songs(xml, min_play_count=5):
    """Parse Apple Music XML and return only favorite songs with play count above threshold."""
    plist = plistlib.loads(xml)
    
    tracks = plist['Tracks']
    favorite_songs = []

    for track_id, track_info in tracks.items():
        name = track_info.get('Name')
        artist = track_info.get('Artist')
        play_count = track_info.get('Play Count', 0)

        if name and play_count >= min_play_count:
            if artist:
                favorite_songs.append(f"{name} {artist}")
            else:
                favorite_songs.append(name)
    
    return favorite_songs

def download_song_from_youtube(query, download_path):
    """Search and download the song from YouTube as an mp3."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'no_warnings': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"[cyan]Searching and downloading:[/] {query}")
            ydl.download([query])
        except Exception as e:
            print(f"[red]Failed to download {query}: {e}[/red]")

def main():
    download_path = os.getenv('SAVE_PATH', '/music/')
    min_play_count = 0

    url = os.getenv('XML_URL')
    r = requests.get(url)
    xml = r.content

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    favorite_songs = parse_favorite_songs(xml, min_play_count)

    print(f"\n[bold yellow]Found {len(favorite_songs)} favorite songs. Starting download...[/bold yellow]\n")

    for song in favorite_songs:
        download_song_from_youtube(song, download_path)

    print("\n[bold green]All downloads finished![/bold green]")

if __name__ == '__main__':
    main()
