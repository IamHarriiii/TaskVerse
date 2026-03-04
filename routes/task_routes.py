"""Task routes — full CRUD with pagination, filtering, and search."""

from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import Optional
from uuid import UUID

from schemas.task_schemas import (
    TaskCreateInput,
    TaskUpdateInput,
    TaskResponse,
    PaginatedTaskResponse,
)
from services.task_service import TaskService
from exceptions import TaskVerseError
from auth import get_current_user_id

router = APIRouter()
task_service = TaskService()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_input: TaskCreateInput,
    current_user_id: UUID = Depends(get_current_user_id),
):
    # Ensure users can only create tasks for themselves
    if task_input.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create tasks for yourself",
        )
    try:
        return task_service.create_task(task_input)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=PaginatedTaskResponse)
def get_all_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[int] = Query(None, ge=1, le=5),
    user_id: Optional[UUID] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None, min_length=1, max_length=200),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List tasks with optional filtering, search, and pagination."""
    return task_service.get_all_tasks(
        status=status_filter,
        priority=priority,
        user_id=user_id,
        tag=tag,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: UUID):
    try:
        return task_service.get_task_by_id(task_id)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    task_input: TaskUpdateInput,
    current_user_id: UUID = Depends(get_current_user_id),
):
    # Verify task ownership
    try:
        existing = task_service.get_task_by_id(task_id)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    if existing.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks",
        )

    try:
        return task_service.update_task(task_id, task_input)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
):
    # Verify task ownership
    try:
        existing = task_service.get_task_by_id(task_id)
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    if existing.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks",
        )

    try:
        task_service.delete_task(task_id)
        return {"detail": "Task deleted"}
    except TaskVerseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)