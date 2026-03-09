from fastapi import APIRouter, HTTPException
from schemas.models import PlaylistRequest, PlaylistResponse
from services.playlist import extract_playlist_urls

router = APIRouter(prefix="/api/playlist", tags=["Playlist"])

@router.post("/extract", response_model=PlaylistResponse)
def get_playlist(request: PlaylistRequest):
    try:
        urls = extract_playlist_urls(str(request.url))
        if not urls:
            raise HTTPException(status_code=404, detail="No videos found or invalid playlist.")
        return PlaylistResponse(
            playlist_url=str(request.url), total_videos=len(urls), video_urls=urls
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")