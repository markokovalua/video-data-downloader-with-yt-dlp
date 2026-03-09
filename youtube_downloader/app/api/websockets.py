from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.state import progress_queues

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/progress/{download_id}")
async def websocket_endpoint(websocket: WebSocket, download_id: str):
    await websocket.accept()

    if download_id not in progress_queues:
        await websocket.close(code=1000)
        return

    try:
        while True:
            data = await progress_queues[download_id].get()
            await websocket.send_json(data)
            if data["status"] == "merging":
                break
    except WebSocketDisconnect:
        pass
    finally:
        if download_id in progress_queues:
            del progress_queues[download_id]