import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from schemas.models import VideoURL
from services.subtitles import sync_download_subtitles

router = APIRouter(tags=["Subtitles"])

@router.post("/download-subtitles/")
async def get_subtitles(video_url: VideoURL):
    try:
        resp = await asyncio.to_thread(sync_download_subtitles, video_url.url)
        return JSONResponse(
            status_code=200, content=resp, headers={"X-Custom-Header": "Value"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))