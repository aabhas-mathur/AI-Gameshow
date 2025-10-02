from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class RoundStatus(str, enum.Enum):
    QUESTION = "question"
    ANSWERING = "answering"
    VOTING = "voting"
    RESULTS = "results"
    COMPLETED = "completed"


class Round(Base):
    __tablename__ = "rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    status = Column(Enum(RoundStatus), default=RoundStatus.QUESTION, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime, nullable=True)

    # Relationships
    room = relationship("Room", back_populates="rounds")
    answers = relationship("Answer", back_populates="round", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="round", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="round", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Round {self.round_number} - Room {self.room_id}>"