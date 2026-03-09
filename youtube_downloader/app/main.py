import logging
from fastapi import FastAPI
from api.routers import media, subtitles, playlist
from api import websockets

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Video Metadata downloading API")

app.include_router(media.router)
app.include_router(subtitles.router)
app.include_router(playlist.router)
app.include_router(websockets.router)