import os
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from schemas.models import VideoURL
from core.state import progress_queues
from services.downloader import sync_download, sync_download_audio
from utils.files import remove_file

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Media Download"])


@router.post("/download/")
async def download_video(video_url: VideoURL, background_tasks: BackgroundTasks):
    try:
        download_id = video_url.download_id
        loop = asyncio.get_running_loop()
        progress_queues[download_id] = asyncio.Queue()

        filepath = await asyncio.to_thread(sync_download, video_url.url, download_id, loop)
        background_tasks.add_task(remove_file, filepath)

        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="video/mp4",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/download-audio/")
async def download_audio(video_url: VideoURL, background_tasks: BackgroundTasks):
    download_id = video_url.download_id
    loop = asyncio.get_running_loop()
    progress_queues[download_id] = asyncio.Queue()

    try:
        filepath = await asyncio.to_thread(sync_download_audio, video_url.url, download_id, loop)
        background_tasks.add_task(remove_file, filepath)

        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="audio/mpeg",
        )
    except Exception as e:
        progress_queues.pop(download_id, None)
        raise HTTPException(status_code=400, detail=str(e))