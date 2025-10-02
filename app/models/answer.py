from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    round_id = Column(UUID(as_uuid=True), ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    round = relationship("Round", back_populates="answers")
    user = relationship("User", back_populates="answers")
    votes = relationship("Vote", back_populates="answer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Answer {self.id[:8]} by User {self.user_id}>"