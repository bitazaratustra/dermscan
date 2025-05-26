from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from ..utils.security import get_current_user


router = APIRouter()

@router.get("", response_model=UserResponse)
def get_user(current_user: UserResponse = Depends(get_current_user)):
    return current_user
