# Spotify Wallpaper

Retrieve top albuns from spotify, download album covers and create a wallpaper.

## Demonstration

### Dark Mode
![wallpaper](https://github.com/user-attachments/assets/9f70a431-5879-4798-9392-29e3f6706576)

### Light Mode
![wallpaper_light](https://github.com/user-attachments/assets/136221ad-ad2a-4106-94d7-e68c8ca1dd97)

## Cron job

Add the following line to your crontab, run once manually to log in spotify account and keep the `.cache` file.

```sh
cd <absolute-path>/spotify-wallpaper && .venv/bin/python3 api.py >> cron.log 2>&1

```
