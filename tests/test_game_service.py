import pytest
from app.services.game_service import GameService
from app.services.room_service import RoomService
from app.services.auth_service import AuthService
from app.schemas.room import RoomCreate
from app.schemas.user import UserCreate
from app.models.room import RoomStatus
from app.utils.exceptions import BadRequestException, ForbiddenException


def test_start_game(db):
    """Test starting a game"""
    # Create host and room
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)

    # Start game
    updated_room = GameService.start_game(room.code, host.id, db)

    assert updated_room.status == RoomStatus.ACTIVE


def test_start_game_non_host(db):
    """Test that non-host cannot start game"""
    # Create host and room
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)

    # Create another user
    user_data = UserCreate(email="user@example.com", username="user", password="pass123")
    user = AuthService.register(user_data, db)

    # Try to start game as non-host
    with pytest.raises(ForbiddenException):
        GameService.start_game(room.code, user.id, db)


def test_submit_answer(db):
    """Test submitting an answer"""
    # Create user and room
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)

    # Start a round
    round_obj = GameService.start_round(room.id, 1, "Test question?", db)

    # Submit answer
    answer = GameService.submit_answer(round_obj.id, host.id, "Test answer", db)

    assert answer.content == "Test answer"
    assert answer.user_id == host.id


def test_submit_duplicate_answer(db):
    """Test that user cannot submit multiple answers for same round"""
    # Create user and room
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)

    # Start a round
    round_obj = GameService.start_round(room.id, 1, "Test question?", db)

    # Submit first answer
    GameService.submit_answer(round_obj.id, host.id, "Answer 1", db)

    # Try to submit second answer
    with pytest.raises(BadRequestException):
        GameService.submit_answer(round_obj.id, host.id, "Answer 2", db)


def test_submit_vote(db):
    """Test submitting a vote"""
    # Create two users
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)

    user_data = UserCreate(email="user@example.com", username="user", password="pass123")
    user = AuthService.register(user_data, db)

    # Create room and round
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)
    round_obj = GameService.start_round(room.id, 1, "Test question?", db)

    # Submit answer from user
    answer = GameService.submit_answer(round_obj.id, user.id, "User answer", db)

    # Transition to voting
    GameService.start_voting(round_obj.id, db)

    # Host votes for user's answer
    vote = GameService.submit_vote(round_obj.id, host.id, answer.id, db)

    assert vote.voter_id == host.id
    assert vote.answer_id == answer.id


def test_cannot_vote_for_own_answer(db):
    """Test that user cannot vote for their own answer"""
    # Create user
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)

    # Create room and round
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)
    round_obj = GameService.start_round(room.id, 1, "Test question?", db)

    # Submit answer
    answer = GameService.submit_answer(round_obj.id, host.id, "My answer", db)

    # Transition to voting
    GameService.start_voting(round_obj.id, db)

    # Try to vote for own answer
    with pytest.raises(BadRequestException):
        GameService.submit_vote(round_obj.id, host.id, answer.id, db)