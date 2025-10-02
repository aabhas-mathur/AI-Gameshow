from fastapi import Depends, Cookie, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database import get_db
from app.utils.security import verify_token
from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.exceptions import AuthenticationException


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from cookie token
    """
    if not access_token:
        raise AuthenticationException("Not authenticated")

    try:
        payload = verify_token(access_token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise AuthenticationException("Invalid token payload")

        user = AuthService.get_user_by_id(user_id, db)
        return user

    except ValueError:
        raise AuthenticationException("Could not validate credentials")
    except Exception as e:
        raise AuthenticationException(f"Authentication error: {str(e)}")


async def get_current_user_optional(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns None if not authenticated
    """
    if not access_token:
        return None

    try:
        payload = verify_token(access_token)
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        user = AuthService.get_user_by_id(user_id, db)
        return user

    except:
        return None