from pydantic import BaseModel

class VideoURL(BaseModel):
    url: str
    download_id: str


class PlaylistRequest(BaseModel):
    url: str  # Pydantic will automatically validate that this is a real URL


# Define what the API will return
class PlaylistResponse(BaseModel):
    playlist_url: str
    total_videos: int
    video_urls: list[str]