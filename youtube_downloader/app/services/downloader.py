# services/downloader.py
import os
import asyncio
import logging
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException
from core.state import progress_queues
from services.subtitles import download_subs_worker

logger = logging.getLogger(__name__)


def sync_download(url: str, download_id: str, loop: asyncio.AbstractEventLoop):
    queue = progress_queues.get(download_id)

    def download_progress_hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            payload = {
                "status": "downloading",
                "downloaded_bytes": downloaded,
                "total_bytes": total,
            }
            if queue:
                asyncio.run_coroutine_threadsafe(queue.put(payload), loop)
        elif d["status"] == "finished":
            if queue:
                asyncio.run_coroutine_threadsafe(queue.put({"status": "merging"}), loop)

    ydl_opts = {
        "outtmpl": "./downloads/%(title)s.%(ext)s",
        "format": "137+140/399+140/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": "/usr/bin/ffmpeg",
        "quiet": False,
        "noplaylist": True,
        "progress_hooks": [download_progress_hook],
        "concurrent_fragment_downloads": 10,
        "buffersize": 1024 * 512,
        "http_chunk_size": 10485760,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "continuedl": True,
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
                    executor.submit(download_subs_worker, ua_url, "./downloads/tmp_ua.srt")
                if en_url:
                    executor.submit(download_subs_worker, en_url, "./downloads/tmp_en.srt")

            filename = ydl.prepare_filename(info)
            ydl.download([url])
            return filename
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")


def sync_download_audio(url: str, download_id: str, loop: asyncio.AbstractEventLoop) -> str:
    ydl_opts = {
        "outtmpl": "./downloads/%(title)s.%(ext)s",
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "ffmpeg_location": "/usr/bin/ffmpeg",
        "quiet": False,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 10,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            base_filename = ydl.prepare_filename(info)
            final_filename = os.path.splitext(base_filename)[0] + ".mp3"
            ydl.download([url])
            return final_filename
        except Exception as e:
            logger.error(f"yt-dlp audio error: {e}")
            raise RuntimeError(f"Audio download failed: {str(e)}")