import pytest
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.utils.exceptions import ConflictException, AuthenticationException


def test_register_user(db):
    """Test user registration"""
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )

    user = AuthService.register(user_data, db)

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.password_hash != "password123"  # Password should be hashed


def test_register_duplicate_email(db):
    """Test registration with duplicate email"""
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )

    AuthService.register(user_data, db)

    # Try to register again with same email
    with pytest.raises(ConflictException):
        AuthService.register(user_data, db)


def test_authenticate_success(db):
    """Test successful authentication"""
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )

    AuthService.register(user_data, db)

    user = AuthService.authenticate("test@example.com", "password123", db)

    assert user.email == "test@example.com"


def test_authenticate_wrong_password(db):
    """Test authentication with wrong password"""
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )

    AuthService.register(user_data, db)

    with pytest.raises(AuthenticationException):
        AuthService.authenticate("test@example.com", "wrongpassword", db)


def test_authenticate_nonexistent_user(db):
    """Test authentication with non-existent user"""
    with pytest.raises(AuthenticationException):
        AuthService.authenticate("nonexistent@example.com", "password123", db)