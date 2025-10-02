import pytest
from app.services.room_service import RoomService
from app.services.auth_service import AuthService
from app.schemas.room import RoomCreate
from app.schemas.user import UserCreate
from app.utils.exceptions import NotFoundException, BadRequestException


def test_create_room(db):
    """Test room creation"""
    # Create a user first
    user_data = UserCreate(email="host@example.com", username="host", password="pass123")
    user = AuthService.register(user_data, db)

    room_data = RoomCreate(max_players=5, total_rounds=3)
    room = RoomService.create_room(room_data, user.id, db)

    assert room.code is not None
    assert len(room.code) == 6
    assert room.host_id == user.id
    assert room.max_players == 5
    assert room.total_rounds == 3


def test_join_room(db):
    """Test joining a room"""
    # Create host and room
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)

    # Create another user and join
    user_data = UserCreate(email="user@example.com", username="user", password="pass123")
    user = AuthService.register(user_data, db)

    joined_room = RoomService.join_room(room.code, user.id, db)

    assert joined_room.id == room.id

    # Check participants
    participants = RoomService.get_room_participants(room.id, db)
    assert len(participants) == 2


def test_join_nonexistent_room(db):
    """Test joining non-existent room"""
    user_data = UserCreate(email="user@example.com", username="user", password="pass123")
    user = AuthService.register(user_data, db)

    with pytest.raises(NotFoundException):
        RoomService.join_room("INVALID", user.id, db)


def test_get_room_participants(db):
    """Test getting room participants"""
    # Create host and room
    host_data = UserCreate(email="host@example.com", username="host", password="pass123")
    host = AuthService.register(host_data, db)
    room_data = RoomCreate()
    room = RoomService.create_room(room_data, host.id, db)

    participants = RoomService.get_room_participants(room.id, db)

    assert len(participants) == 1
    assert participants[0].id == host.id