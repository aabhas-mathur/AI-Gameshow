from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from app.models.room import Room, RoomStatus
from app.models.round import Round, RoundStatus
from app.models.answer import Answer
from app.models.vote import Vote
from app.models.score import Score
from app.utils.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class GameService:
    @staticmethod
    def start_game(room_code: str, user_id: UUID, db: Session) -> Room:
        """Start a game (only host can start)"""
        room = db.query(Room).filter(Room.code == room_code).first()

        if not room:
            raise NotFoundException("Room not found")

        # Convert user_id to UUID if it's a string
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        if room.host_id != user_id:
            raise ForbiddenException("Only the host can start the game")

        if room.status != RoomStatus.WAITING:
            raise BadRequestException("Game already started or finished")

        room.status = RoomStatus.ACTIVE
        db.commit()

        logger.info(f"Game started in room {room_code}")
        return room

    @staticmethod
    def start_round(room_id: UUID, round_number: int, question: str, db: Session) -> Round:
        """Start a new round"""
        room = db.query(Room).filter(Room.id == room_id).first()

        if not room:
            raise NotFoundException("Room not found")

        new_round = Round(
            room_id=room_id,
            round_number=round_number,
            question=question,
            status=RoundStatus.ANSWERING,
            ends_at=datetime.utcnow() + timedelta(seconds=settings.ANSWER_TIME_LIMIT)
        )

        db.add(new_round)
        room.current_round = round_number
        db.commit()
        db.refresh(new_round)

        logger.info(f"Round {round_number} started in room {room.code}")
        return new_round

    @staticmethod
    def submit_answer(round_id: UUID, user_id: UUID, content: str, db: Session) -> Answer:
        """Submit an answer for a round"""
        round_obj = db.query(Round).filter(Round.id == round_id).first()

        if not round_obj:
            raise NotFoundException("Round not found")

        if round_obj.status != RoundStatus.ANSWERING:
            raise BadRequestException("Not accepting answers at this time")

        # Check if user already submitted
        existing_answer = db.query(Answer).filter(
            Answer.round_id == round_id,
            Answer.user_id == user_id
        ).first()

        if existing_answer:
            raise BadRequestException("Already submitted an answer for this round")

        answer = Answer(
            round_id=round_id,
            user_id=user_id,
            content=content
        )

        db.add(answer)
        db.commit()
        db.refresh(answer)

        logger.info(f"Answer submitted by user {user_id} for round {round_id}")
        return answer

    @staticmethod
    def start_voting(round_id: UUID, db: Session) -> Round:
        """Transition round to voting phase"""
        round_obj = db.query(Round).filter(Round.id == round_id).first()

        if not round_obj:
            raise NotFoundException("Round not found")

        round_obj.status = RoundStatus.VOTING
        round_obj.ends_at = datetime.utcnow() + timedelta(seconds=settings.VOTE_TIME_LIMIT)
        db.commit()

        logger.info(f"Voting started for round {round_id}")
        return round_obj

    @staticmethod
    def submit_vote(round_id: UUID, voter_id: UUID, answer_id: UUID, db: Session) -> Vote:
        """Submit a vote for an answer"""
        round_obj = db.query(Round).filter(Round.id == round_id).first()

        if not round_obj:
            raise NotFoundException("Round not found")

        if round_obj.status != RoundStatus.VOTING:
            raise BadRequestException("Not accepting votes at this time")

        # Get the answer
        answer = db.query(Answer).filter(Answer.id == answer_id).first()

        if not answer:
            raise NotFoundException("Answer not found")

        # Prevent self-voting
        if answer.user_id == voter_id:
            raise BadRequestException("Cannot vote for your own answer")

        # Check if user already voted
        existing_vote = db.query(Vote).filter(
            Vote.round_id == round_id,
            Vote.voter_id == voter_id
        ).first()

        if existing_vote:
            raise BadRequestException("Already voted in this round")

        vote = Vote(
            round_id=round_id,
            voter_id=voter_id,
            answer_id=answer_id
        )

        db.add(vote)
        db.commit()
        db.refresh(vote)

        # Update score
        GameService._update_score(round_obj.room_id, answer.user_id, round_id, db)

        logger.info(f"Vote submitted by user {voter_id} for answer {answer_id}")
        return vote

    @staticmethod
    def _update_score(room_id: UUID, user_id: UUID, round_id: UUID, db: Session):
        """Update score for a user"""
        score = db.query(Score).filter(
            Score.room_id == room_id,
            Score.user_id == user_id,
            Score.round_id == round_id
        ).first()

        if not score:
            score = Score(
                room_id=room_id,
                user_id=user_id,
                round_id=round_id,
                points=1
            )
            db.add(score)
        else:
            score.points += 1

        db.commit()

    @staticmethod
    def end_round(round_id: UUID, db: Session) -> Round:
        """End a round and show results"""
        round_obj = db.query(Round).filter(Round.id == round_id).first()

        if not round_obj:
            raise NotFoundException("Round not found")

        round_obj.status = RoundStatus.COMPLETED
        db.commit()

        logger.info(f"Round {round_id} completed")
        return round_obj

    @staticmethod
    def get_round_answers(round_id: UUID, db: Session) -> List[Answer]:
        """Get all answers for a round"""
        answers = db.query(Answer).filter(Answer.round_id == round_id).all()
        return answers

    @staticmethod
    def get_leaderboard(room_id: UUID, db: Session) -> List[Dict[str, Any]]:
        """Get leaderboard for a room"""
        from app.models.user import User

        results = db.query(
            Score.user_id,
            User.username,
            func.sum(Score.points).label('total_points')
        ).join(
            User, Score.user_id == User.id
        ).filter(
            Score.room_id == room_id
        ).group_by(
            Score.user_id,
            User.username
        ).order_by(
            func.sum(Score.points).desc()
        ).all()

        leaderboard = []
        for result in results:
            leaderboard.append({
                'user_id': str(result.user_id),
                'username': result.username,
                'score': result.total_points or 0
            })

        return leaderboard

    @staticmethod
    def end_game(room_id: UUID, db: Session):
        """End the game"""
        room = db.query(Room).filter(Room.id == room_id).first()

        if room:
            room.status = RoomStatus.FINISHED
            db.commit()
            logger.info(f"Game ended in room {room.code}")

    @staticmethod
    def get_answer_vote_count(answer_id: UUID, db: Session) -> int:
        """Get vote count for an answer"""
        count = db.query(Vote).filter(Vote.answer_id == answer_id).count()
        return count