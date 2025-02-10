import spotipy, os, requests, shutil, datetime
from spotipy.oauth2 import SpotifyOAuth
from colorama import Fore, Style
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

TIME_RANGE = os.getenv('TIME_RANGE')
IMAGES_DIR = 'images'
WALLPAPERS_DIR = 'wallpapers'

def colorize(text, color):
    return f"{color}{text}{Style.RESET_ALL}"

def get_unique_images():
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    SCOPE = 'user-library-read user-top-read user-read-recently-played user-read-playback-state'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))

    unique_images = set()

    now_playing = sp.current_playback()
    if now_playing and now_playing['is_playing']:
        track_name = now_playing['item']['name']
        artists = ', '.join([artist['name'] for artist in now_playing['item']['artists']])
        print(colorize(f"\nNow Playing: {track_name} - {artists}", Fore.MAGENTA))

    top_artists = sp.current_user_top_artists(limit=5, time_range=TIME_RANGE)
    print(colorize("\nTop 5 Artists:", Fore.MAGENTA))
    for idx, artist in enumerate(top_artists['items'], 1):
        print(f"{idx}. {colorize(artist['name'], Fore.CYAN)}")
        print(artist["images"][0]["url"])
        # unique_images.add(artist["images"][0]["url"])

    top_tracks = sp.current_user_top_tracks(limit=5, time_range=TIME_RANGE)
    print(colorize("\nTop 5 Songs:", Fore.MAGENTA))
    for idx, song in enumerate(top_tracks['items'], 1):
        artists = ', '.join([artist['name'] for artist in song['artists']])
        print(f"{idx}. {colorize(song['name'], Fore.CYAN)} - {colorize(artists, Fore.GREEN)}")
        print(song['album']['images'][0]['url'])
        unique_images.add(song['album']['images'][0]['url'])

    top_tracks = sp.current_user_top_tracks(limit=50, time_range=TIME_RANGE)

    # Extract unique albums from top tracks
    unique_albums = {}
    for track in top_tracks['items']:
        album = track['album']
        album_id = album['id']
        if album_id not in unique_albums:
            unique_albums[album_id] = {
                'name': album['name'],
                'artists': ', '.join([artist['name'] for artist in album['artists']]),
                'image_url': album['images'][0]['url'] if album['images'] else None
            }

    # Print top 5 unique albums
    print(colorize("\nTop 5 Albums:", Fore.MAGENTA))
    for idx, album in enumerate(list(unique_albums.values())[:5], 1):
        print(f"{idx}. {colorize(album['name'], Fore.CYAN)} - {colorize(album['artists'], Fore.GREEN)}")
        if album['image_url']:
            print(album['image_url'])
            unique_images.add(album['image_url'])


    recently_played = sp.current_user_recently_played(limit=5)
    print(colorize("\nTop 5 Recently Played Songs:", Fore.MAGENTA))
    for idx, track in enumerate(recently_played['items'], 1):
        artists = ', '.join([artist['name'] for artist in track['track']['artists']])
        print(f"{idx}. {colorize(track['track']['name'], Fore.CYAN)} - {colorize(artists, Fore.GREEN)}")
        print(track["track"]["album"]["images"][0]["url"])
        unique_images.add(track["track"]["album"]["images"][0]["url"])

    return unique_images

def clean_images_dir():
    if os.path.exists(IMAGES_DIR):
        shutil.rmtree('images', ignore_errors=True)

def download_images(images):
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    
    for image_url in images:
        img_data = requests.get(image_url).content
        with open(f"{IMAGES_DIR}/{image_url.split('/')[-1]}.jpg", 'wb+') as handler:
            handler.write(img_data)
            
def create_wallpaper():
    base_img = Image.open('base.png').convert('RGBA')
    base_img_light = Image.open('base-light.png').convert('RGBA')
    album_covers = [Image.open(f"{IMAGES_DIR}/{image}").convert('RGBA') for image in os.listdir(IMAGES_DIR)]
    album_size = int(base_img.height / 4);

    i = 0
    for album_cover in album_covers:
        album_cover = album_cover.resize((album_size, album_size))
        center_offset = ((base_img.width - album_cover.width) // 2, (base_img.height - album_cover.height) // 2)
        offset = (
            (album_size * i) + (20 * i) + 100 if i > 0 else 100,
            (center_offset[1]) + (40 if i % 2 else -40),
        )

        base_img.paste(album_cover, offset)
        base_img_light.paste(album_cover, offset)
        i += 1

    if not os.path.exists(WALLPAPERS_DIR):
        os.makedirs(WALLPAPERS_DIR)

    base_img.save(f'{WALLPAPERS_DIR}/wallpaper_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')
    base_img_light.save(f'{WALLPAPERS_DIR}/wallpaper_light_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')
    base_img.save('wallpaper.png')
    base_img_light.save('wallpaper_light.png')

def set_wallpaper():
    try:
        from PyWallpaper import change_wallpaper
        change_wallpaper('wallpaper.png')
    except Exception as e:
        os.system(
            f'gsettings set org.gnome.desktop.background picture-uri-dark "file://{os.path.abspath("wallpaper.png")}"'
        )
        os.system(
            f'gsettings set org.gnome.desktop.background picture-uri "file://{os.path.abspath("wallpaper_light.png")}"'
        )

def main():
    unique_images = get_unique_images()
    clean_images_dir()
    download_images(unique_images)
    create_wallpaper()
    set_wallpaper()

if __name__ == "__main__":
    main()
