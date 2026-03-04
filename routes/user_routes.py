"""User routes — CRUD + user-specific task listing."""

from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID

from schemas.user_schemas import UserCreateInput, UserUpdateInput, UserResponse
from schemas.task_schemas import TaskResponse
from services.user_service import UserService
from services.task_service import TaskService
from exceptions import TaskVerseError
from auth import get_current_user_id

router = APIRouter()
user_service = UserService()
task_service = TaskService()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_input: UserCreateInput):
    try:
        return user_service.create_user(user_input)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=list[UserResponse])
def get_all_users():
    return user_service.get_all_users()


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user_id: UUID = Depends(get_current_user_id)):
    """Return the currently authenticated user's profile."""
    try:
        return user_service.get_user_by_id(current_user_id)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: UUID):
    try:
        return user_service.get_user_by_id(user_id)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_input: UserUpdateInput,
    current_user_id: UUID = Depends(get_current_user_id),
):
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )
    try:
        return user_service.update_user(user_id, user_input)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
):
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )
    try:
        user_service.delete_user(user_id)
        return {"detail": "User and associated tasks deleted"}
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
def get_user_tasks(user_id: UUID):
    """Get all tasks assigned to a specific user."""
    try:
        return task_service.get_tasks_by_user(user_id)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)