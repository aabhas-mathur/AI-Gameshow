from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.game import (
    AnswerSubmit, AnswerResponse, VoteSubmit,
    RoundResponse, LeaderboardResponse, ScoreResponse
)
from app.services.game_service import GameService
from app.services.room_service import RoomService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/game", tags=["Game"])


@router.post("/{room_code}/start")
async def start_game(
    room_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start the game (host only)"""
    room = GameService.start_game(room_code, current_user.id, db)
    return {"message": "Game started", "room_code": room.code}


@router.post("/rounds/{round_id}/answer", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    round_id: UUID,
    answer_data: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an answer for a round"""
    answer = GameService.submit_answer(round_id, current_user.id, answer_data.content, db)
    return AnswerResponse(
        id=answer.id,
        content=answer.content,
        vote_count=0,
        is_own_answer=True
    )


@router.get("/rounds/{round_id}/answers", response_model=List[AnswerResponse])
async def get_round_answers(
    round_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all answers for a round"""
    answers = GameService.get_round_answers(round_id, db)

    response = []
    for answer in answers:
        vote_count = GameService.get_answer_vote_count(answer.id, db)
        response.append(AnswerResponse(
            id=answer.id,
            content=answer.content,
            vote_count=vote_count,
            is_own_answer=(answer.user_id == current_user.id)
        ))

    return response


@router.post("/rounds/{round_id}/vote", status_code=status.HTTP_201_CREATED)
async def submit_vote(
    round_id: UUID,
    vote_data: VoteSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a vote for an answer"""
    vote = GameService.submit_vote(round_id, current_user.id, vote_data.answer_id, db)
    return {"message": "Vote submitted", "vote_id": str(vote.id)}


@router.get("/{room_code}/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    room_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard for a room"""
    room = RoomService.get_room(room_code, db)
    leaderboard_data = GameService.get_leaderboard(room.id, db)

    # Get user details
    scores = []
    for entry in leaderboard_data:
        user = db.query(User).filter(User.id == entry['user_id']).first()
        if user:
            scores.append(ScoreResponse(
                user_id=user.id,
                username=user.username,
                total_points=entry['total_points'],
                round_points=0
            ))

    return LeaderboardResponse(scores=scores)