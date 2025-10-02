from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from app.models.round import RoundStatus


class AnswerSubmit(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)


class AnswerResponse(BaseModel):
    id: UUID
    content: str
    vote_count: int = 0
    is_own_answer: bool = False

    class Config:
        from_attributes = True


class VoteSubmit(BaseModel):
    answer_id: UUID


class RoundResponse(BaseModel):
    id: UUID
    round_number: int
    question: str
    status: RoundStatus
    started_at: datetime
    ends_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoundWithAnswers(RoundResponse):
    answers: List[AnswerResponse] = []


class ScoreResponse(BaseModel):
    user_id: UUID
    username: str
    total_points: int
    round_points: int = 0

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    scores: List[ScoreResponse]


class GameStateResponse(BaseModel):
    room_code: str
    status: str
    current_round: int
    total_rounds: int
    round_data: Optional[RoundResponse] = None