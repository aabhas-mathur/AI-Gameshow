from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import AuthResponse
from app.services.auth_service import AuthService
from app.utils.security import create_access_token
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Register a new user"""
    user = AuthService.register(user_data, db)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set httponly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Required for cross-domain cookies
        samesite="none",  # Required for cross-domain cookies
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return AuthResponse(user=UserResponse.model_validate(user), message="Registration successful")


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login user"""
    user = AuthService.authenticate(credentials.email, credentials.password, db)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set httponly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Required for cross-domain cookies
        samesite="none",  # Required for cross-domain cookies
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return AuthResponse(user=UserResponse.model_validate(user), message="Login successful")


@router.post("/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie(key="access_token", secure=True, samesite="none")
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse.model_validate(current_user)
