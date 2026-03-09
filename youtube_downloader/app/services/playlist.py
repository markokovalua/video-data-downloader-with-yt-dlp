import yt_dlp

def extract_playlist_urls(playlist_url: str) -> list[str]:
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            if "entries" in info:
                return [entry["url"] for entry in info["entries"] if entry.get("url")]
            return []
    except Exception as e:
        raise Exception(str(e))