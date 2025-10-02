from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint('round_id', 'voter_id', name='uq_round_voter'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    round_id = Column(UUID(as_uuid=True), ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False)
    voter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    answer_id = Column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    round = relationship("Round", back_populates="votes")
    voter = relationship("User", back_populates="votes")
    answer = relationship("Answer", back_populates="votes")

    def __repr__(self):
        return f"<Vote voter={self.voter_id} answer={self.answer_id}>"