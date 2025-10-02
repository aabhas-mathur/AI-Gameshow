from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hosted_rooms = relationship("Room", back_populates="host", foreign_keys="Room.host_id")
    room_participants = relationship("RoomParticipant", back_populates="user")
    answers = relationship("Answer", back_populates="user")
    votes = relationship("Vote", back_populates="voter")
    scores = relationship("Score", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"