from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import user_model


def is_user_exist(username: str, active_status: bool, db: Session):
    user = (
        db.query(user_model.User)
        .filter(
            user_model.User.username == username,
            user_model.User.is_active == active_status,
        )
        .first()
    )
    if not user:
        if active_status:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User '{username}' not found or deactivated",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User '{username}' is already in active.",
            )
    return user
