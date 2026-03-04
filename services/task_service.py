"""Task service — business logic for task CRUD operations."""

import logging
from datetime import datetime, timezone
from typing import List, Any, Optional
from uuid import UUID

from models.task import Task
from schemas.task_schemas import TaskCreateInput, TaskUpdateInput
from services.storage_service import StorageService
from exceptions import NotFoundError

logger = logging.getLogger("taskverse.services.task")


class TaskService:
    # ── Create ──────────────────────────────────────────────
    def create_task(self, task_input: TaskCreateInput) -> Task:
        data = StorageService.load()

        user_exists = any(
            user["id"] == str(task_input.user_id) for user in data["users"]
        )
        if not user_exists:
            raise NotFoundError("User", str(task_input.user_id))

        new_task = Task(**task_input.model_dump())
        data["tasks"].append(new_task.model_dump())
        StorageService.save(data)
        logger.info("Created task '%s' (id=%s)", new_task.title, new_task.id)
        return new_task

    # ── Read ────────────────────────────────────────────────
    def get_all_tasks(
        self,
        *,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        user_id: Optional[UUID] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return filtered, paginated tasks with metadata."""
        data = StorageService.load()
        tasks = data["tasks"]

        # ── Filters ──
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        if priority is not None:
            tasks = [t for t in tasks if t.get("priority") == priority]
        if user_id:
            tasks = [t for t in tasks if t.get("user_id") == str(user_id)]
        if tag:
            tasks = [t for t in tasks if tag in t.get("tags", [])]
        if search:
            q = search.lower()
            tasks = [
                t
                for t in tasks
                if q in t.get("title", "").lower()
                or q in (t.get("description") or "").lower()
            ]

        total = len(tasks)
        tasks = tasks[skip : skip + limit]

        return {
            "tasks": [Task(**t) for t in tasks],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def get_task_by_id(self, task_id: UUID) -> Task:
        data = StorageService.load()
        for task in data["tasks"]:
            if task["id"] == str(task_id):
                return Task(**task)
        raise NotFoundError("Task", str(task_id))

    def get_tasks_by_user(self, user_id: UUID) -> List[Task]:
        data = StorageService.load()

        user_exists = any(u["id"] == str(user_id) for u in data["users"])
        if not user_exists:
            raise NotFoundError("User", str(user_id))

        return [Task(**t) for t in data["tasks"] if t["user_id"] == str(user_id)]

    # ── Update ──────────────────────────────────────────────
    def update_task(self, task_id: UUID, task_input: TaskUpdateInput) -> Task:
        data = StorageService.load()

        for task in data["tasks"]:
            if task["id"] == str(task_id):
                for key, value in task_input.model_dump(exclude_unset=True).items():
                    task[key] = value if not isinstance(value, list) else [
                        v.model_dump() if hasattr(v, "model_dump") else v
                        for v in value
                    ] if isinstance(value, list) and value and hasattr(value[0], "model_dump") else value
                task["updated_at"] = datetime.now(timezone.utc)

                StorageService.save(data)
                logger.info("Updated task %s", task_id)
                return Task(**task)

        raise NotFoundError("Task", str(task_id))

    # ── Delete ──────────────────────────────────────────────
    def delete_task(self, task_id: UUID) -> bool:
        data = StorageService.load()
        tasks = data["tasks"]
        for i, task in enumerate(tasks):
            if task["id"] == str(task_id):
                del tasks[i]
                StorageService.save(data)
                logger.info("Deleted task %s", task_id)
                return True
        raise NotFoundError("Task", str(task_id))