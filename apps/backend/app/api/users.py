from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

