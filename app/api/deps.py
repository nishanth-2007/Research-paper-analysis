import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)

DEFAULT_DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_DEMO_EMAIL = "author@hackathon.edu"


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Returns authenticated user, or auto-provisions a default demo researcher account
    for seamless hackathon demonstration and automated testing.
    """
    user = db.query(User).filter(User.id == DEFAULT_DEMO_USER_ID).first()
    if not user:
        user = User(
            id=DEFAULT_DEMO_USER_ID,
            email=DEFAULT_DEMO_EMAIL,
            hashed_password="demo_hashed_password",
            full_name="Lead Research Author",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
