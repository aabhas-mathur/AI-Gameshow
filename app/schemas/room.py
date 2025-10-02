from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from app.models.room import RoomStatus
from app.schemas.user import UserInRoom


class RoomCreate(BaseModel):
    max_players: int = Field(default=8, ge=2, le=20)
    total_rounds: int = Field(default=5, ge=1, le=10)


class RoomJoin(BaseModel):
    code: str = Field(..., min_length=6, max_length=10)


class RoomResponse(BaseModel):
    id: UUID
    code: str
    host_id: UUID
    status: RoomStatus
    max_players: int
    total_rounds: int
    current_round: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoomDetailResponse(RoomResponse):
    participants: List[UserInRoom] = []
    participant_count: int

    class Config:
        from_attributes = True