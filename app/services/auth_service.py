from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import hash_password, verify_password
from app.utils.exceptions import AuthenticationException, ConflictException
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    @staticmethod
    def register(user_data: UserCreate, db: Session) -> User:
        """Register a new user"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise ConflictException("Email already registered")

        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"New user registered: {new_user.email}")
        return new_user

    @staticmethod
    def authenticate(email: str, password: str, db: Session) -> User:
        """Authenticate a user"""
        user = db.query(User).filter(User.email == email).first()

        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise AuthenticationException("Invalid email or password")

        if not verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {email}")
            raise AuthenticationException("Invalid email or password")

        logger.info(f"User authenticated: {user.email}")
        return user

    @staticmethod
    def get_user_by_id(user_id: str, db: Session) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AuthenticationException("User not found")
        return user