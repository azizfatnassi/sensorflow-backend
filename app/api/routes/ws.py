


from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from app.core.config import settings
from app.websocket.manager import manager

router=APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket:WebSocket,
    token:str=Query(...)
):
    
    try:
        payload=jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email=payload.get("sub")
        if email is None:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
    
    await manager.connect(websocket)

    try:
        while True:
            data=await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    