import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Any
from uuid import UUID

from models.task import Task
from schemas.task_schemas import TaskCreateInput, TaskUpdateInput

DATA_FILE_PATH = Path("storage/data.json")

class TaskService:
    def _load_data(self) -> dict[str, Any]:
        with open(DATA_FILE_PATH, "r") as file:
            return json.load(file)

    def _save_data(self, data: dict[str, Any]) -> None:
        with open(DATA_FILE_PATH, "w") as file:
            json.dump(data, file, default=str, indent=2)

    def create_task(self, task_input: TaskCreateInput) -> Task:
        data = self._load_data()

        user_exists = any(
            user["id"] == str(task_input.user_id)
            for user in data["users"]
        )

        if not user_exists:
            raise ValueError("User does not exist")

        new_task = Task(**task_input.model_dump())

        tasks_list: list[dict[str, Any]] = data["tasks"]
        tasks_list.append(new_task.model_dump())

        self._save_data(data)
        return new_task

    def get_all_tasks(self) -> List[Task]:
        data = self._load_data()
        return [Task(**task) for task in data["tasks"]]

    def update_task(self, task_id: UUID, task_input: TaskUpdateInput) -> Task | None:
        data = self._load_data()

        for task in data["tasks"]:
            if task["id"] == str(task_id):
                for key, value in task_input.model_dump(exclude_unset=True).items():
                    task[key] = value
                task["updated_at"] = datetime.now(timezone.utc)

                self._save_data(data)
                return Task(**task)

        return None

    def delete_task(self, task_id: UUID) -> bool:
        data = self._load_data()
        tasks = data["tasks"]
        for i, task in enumerate(tasks):
            if task["id"] == str(task_id):
                del tasks[i]
                self._save_data(data)
                return True
        return False