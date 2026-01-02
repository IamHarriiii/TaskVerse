from fastapi import APIRouter, HTTPException, status
from uuid import UUID

from schemas.task_schemas import (
    TaskCreateInput,
    TaskUpdateInput,
    TaskResponse,
)
from services.task_service import TaskService

router = APIRouter()
task_service = TaskService()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_input: TaskCreateInput):
    try:
        return task_service.create_task(task_input)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/", response_model=list[TaskResponse])
def get_all_tasks():
    return task_service.get_all_tasks()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, task_input: TaskUpdateInput):
    task = task_service.update_task(task_id, task_input)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(task_id: UUID):
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}