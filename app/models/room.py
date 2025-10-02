from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class RoomStatus(str, enum.Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    FINISHED = "finished"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    host_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(RoomStatus), default=RoomStatus.WAITING, nullable=False)
    max_players = Column(Integer, default=8)
    total_rounds = Column(Integer, default=5)
    current_round = Column(Integer, default=0)
    questions = Column(JSON, default=list)  # Store pre-generated questions
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    host = relationship("User", back_populates="hosted_rooms", foreign_keys=[host_id])
    participants = relationship("RoomParticipant", back_populates="room", cascade="all, delete-orphan")
    rounds = relationship("Round", back_populates="room", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Room {self.code} - {self.status}>"


class RoomParticipant(Base):
    __tablename__ = "room_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="participants")
    user = relationship("User", back_populates="room_participants")

    def __repr__(self):
        return f"<RoomParticipant room={self.room_id} user={self.user_id}>"