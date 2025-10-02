from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.room import RoomCreate, RoomJoin, RoomResponse, RoomDetailResponse
from app.schemas.user import UserInRoom
from app.services.room_service import RoomService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/rooms", tags=["Rooms"])


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new game room"""
    room = RoomService.create_room(room_data, current_user.id, db)
    return RoomResponse.model_validate(room)


@router.post("/join", response_model=RoomResponse)
async def join_room(
    join_data: RoomJoin,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join an existing room"""
    room = RoomService.join_room(join_data.code, current_user.id, db)

    # Get updated participant list
    participants = RoomService.get_room_participants(room.id, db)

    # Emit WebSocket event to notify all users in the room
    try:
        from app.websocket.events import sio
        await sio.emit('player_joined', {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'participant_count': len(participants),
            'participants': [{'id': str(p.id), 'username': p.username} for p in participants]
        }, room=join_data.code)
    except Exception as e:
        # Log but don't fail the request if WebSocket emission fails
        print(f"WebSocket emission failed: {e}")

    return RoomResponse.model_validate(room)


@router.get("/{room_code}", response_model=RoomDetailResponse)
async def get_room(
    room_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get room details"""
    room = RoomService.get_room(room_code, db)
    participants = RoomService.get_room_participants(room.id, db)

    return RoomDetailResponse(
        **RoomResponse.model_validate(room).model_dump(),
        participants=[UserInRoom.model_validate(p) for p in participants],
        participant_count=len(participants)
    )


@router.delete("/{room_code}/leave")
async def leave_room(
    room_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a room"""
    RoomService.leave_room(room_code, current_user.id, db)

    # Get room to check participant count
    try:
        room = RoomService.get_room(room_code, db)
        participants = RoomService.get_room_participants(room.id, db)

        # Emit WebSocket event to notify remaining users
        from app.websocket.events import sio
        await sio.emit('player_left', {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'participant_count': len(participants),
            'participants': [{'id': str(p.id), 'username': p.username} for p in participants]
        }, room=room_code)
    except Exception as e:
        print(f"WebSocket emission failed: {e}")

    return {"message": "Left room successfully"}