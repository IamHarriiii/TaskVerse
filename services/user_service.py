import json
from pathlib import Path
from typing import List, Any
from uuid import UUID

from models.user import User
from schemas.user_schemas import UserCreateInput

DATA_FILE_PATH = Path("storage/data.json")

class UserService:
    def __init__(self) -> None:
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self) -> None:
        if not DATA_FILE_PATH.exists():
            DATA_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_FILE_PATH, "w") as file:
                json.dump({"users": [], "tasks": []}, file)

    def _load_data(self) -> dict[str, Any]:
        if not DATA_FILE_PATH.exists():
            # If the file does not exist, treat as empty data
            return {"users": [], "tasks": []}
        try:
            with open(DATA_FILE_PATH, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # Corrupted or empty file – reset to empty structure
            return {"users": [], "tasks": []}
        
    def _save_data(self, data: dict[str, Any]) -> None:
        with open(DATA_FILE_PATH, "w") as file:
            json.dump(data, file, default=str, indent=2)

    def create_user(self, user_input: UserCreateInput) -> User:
        data = self._load_data()
        # Check for duplicate email
        if any(u["email"] == user_input.email for u in data["users"]):
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        new_user = User(**user_input.model_dump())
        users_list: list[dict[str, Any]] = data["users"]
        users_list.append(new_user.model_dump())
        self._save_data(data)
        return new_user

    def get_all_users(self) -> List[User]:
        data = self._load_data()
        return [User(**user) for user in data["users"]]

    def get_user_by_id(self, user_id: UUID) -> User | None:
        data = self._load_data()
        for user in data["users"]:
            if user["id"] == str(user_id):
                return User(**user)
        return None

    def delete_user(self, user_id: UUID) -> bool:
        data = self._load_data()
        users = data["users"]
        for i, user in enumerate(users):
            if user["id"] == str(user_id):
                del users[i]
                self._save_data(data)
                return True
        return False