from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from app.models.room import Room, RoomParticipant, RoomStatus
from app.models.user import User
from app.schemas.room import RoomCreate
from app.utils.room_code import generate_room_code
from app.utils.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RoomService:
    @staticmethod
    def create_room(room_data: RoomCreate, host_id: UUID, db: Session) -> Room:
        """Create a new game room"""
        # Generate unique room code
        while True:
            code = generate_room_code()
            existing_room = db.query(Room).filter(Room.code == code).first()
            if not existing_room:
                break

        new_room = Room(
            code=code,
            host_id=host_id,
            max_players=room_data.max_players,
            total_rounds=room_data.total_rounds,
            status=RoomStatus.WAITING
        )

        db.add(new_room)
        db.commit()
        db.refresh(new_room)

        # Add host as first participant
        participant = RoomParticipant(
            room_id=new_room.id,
            user_id=host_id
        )
        db.add(participant)
        db.commit()

        logger.info(f"Room created: {new_room.code} by user {host_id}")
        return new_room

    @staticmethod
    def join_room(room_code: str, user_id: UUID, db: Session) -> Room:
        """Join an existing room"""
        room = db.query(Room).filter(Room.code == room_code).first()

        if not room:
            raise NotFoundException(f"Room with code {room_code} not found")

        if room.status != RoomStatus.WAITING:
            raise BadRequestException("Room is not accepting new players")

        # Check if user already in room
        existing_participant = db.query(RoomParticipant).filter(
            RoomParticipant.room_id == room.id,
            RoomParticipant.user_id == user_id
        ).first()

        if existing_participant:
            return room

        # Check room capacity
        participant_count = db.query(RoomParticipant).filter(
            RoomParticipant.room_id == room.id
        ).count()

        if participant_count >= room.max_players:
            raise BadRequestException("Room is full")

        # Add participant
        participant = RoomParticipant(
            room_id=room.id,
            user_id=user_id
        )
        db.add(participant)
        db.commit()

        logger.info(f"User {user_id} joined room {room_code}")
        return room

    @staticmethod
    def get_room(room_code: str, db: Session) -> Room:
        """Get room by code"""
        room = db.query(Room).filter(Room.code == room_code).first()
        if not room:
            raise NotFoundException(f"Room with code {room_code} not found")
        return room

    @staticmethod
    def get_room_participants(room_id: UUID, db: Session) -> List[User]:
        """Get all participants in a room"""
        participants = db.query(User).join(
            RoomParticipant, RoomParticipant.user_id == User.id
        ).filter(
            RoomParticipant.room_id == room_id
        ).all()

        return participants

    @staticmethod
    def leave_room(room_code: str, user_id: UUID, db: Session):
        """Leave a room"""
        room = db.query(Room).filter(Room.code == room_code).first()
        if not room:
            raise NotFoundException(f"Room with code {room_code} not found")

        participant = db.query(RoomParticipant).filter(
            RoomParticipant.room_id == room.id,
            RoomParticipant.user_id == user_id
        ).first()

        if participant:
            db.delete(participant)
            db.commit()
            logger.info(f"User {user_id} left room {room_code}")

    @staticmethod
    def update_room_status(room_id: UUID, status: RoomStatus, db: Session):
        """Update room status"""
        room = db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.status = status
            db.commit()
            logger.info(f"Room {room.code} status updated to {status}")