from fastapi import APIRouter, HTTPException, status
from uuid import UUID

from schemas.user_schemas import UserCreateInput, UserResponse
from services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_input: UserCreateInput):
    return user_service.create_user(user_input)


@router.get("/", response_model=list[UserResponse])
def get_all_users():
    return user_service.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: UUID):
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID):
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}