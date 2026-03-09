# services/subtitles.py
import os
import requests
import logging
import yt_dlp
from http.cookiejar import MozillaCookieJar
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException
from utils.remove_redundant import optimize_srt_cleaning

logger = logging.getLogger(__name__)

def download_subtitles(url: str, output_path: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            response.encoding = "utf-8"
            content = response.text
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.error(f"Subtitles saved into: {output_path}")
            return content
        elif response.status_code == 429:
            logger.error("Too much requests.")
        else:
            logger.error(f"Error {response.status_code}: {response.reason}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")

def download_subs_worker(url, output_path):
    session = requests.Session()
    try:
        cj = MozillaCookieJar("www.youtube.com_cookies.txt")
        cj.load(ignore_discard=True, ignore_expires=True)
        session.cookies = cj

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,uk;q=0.8",
            "Referer": "https://www.youtube.com/",
        }

        resp = session.get(url, headers=headers, proxies={}, timeout=15)
        logger.error(f"Subtitle download response status: {resp.status_code}")
        resp.raise_for_status()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        return resp.text
    except Exception as ce:
        logger.error(f"Could not load cookies: {ce}")

def sync_download_subtitles(url: str):
    ydl_opts = {
        "outtmpl": "./downloads/%(title)s.%(ext)s",
        "format": "137+140/399+140/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": "/usr/bin/ffmpeg",
        "quiet": False,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            available_auto_subs = info.get("automatic_captions")
            ua_url = available_auto_subs.get("uk")[-2]["url"]
            en_url = available_auto_subs.get("en")[-2]["url"]
            logger.error(f"ua_url {ua_url} en_url {en_url}")
            with ThreadPoolExecutor(max_workers=2) as executor:
                if ua_url:
                    ua_resp = download_subs_worker(ua_url, "./downloads/tmp_ua.srt")
                if en_url:
                    en_resp = download_subs_worker(en_url, "./downloads/tmp_en.srt")

            return {
                "ua_resp": optimize_srt_cleaning(ua_resp or ""),
                "en_resp": optimize_srt_cleaning(en_resp or ""),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing subtitles: {str(e)}")
