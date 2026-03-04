"""User service — business logic for user CRUD operations."""

import logging
from typing import List, Any
from uuid import UUID

from models.user import User
from schemas.user_schemas import UserCreateInput, UserUpdateInput
from services.storage_service import StorageService
from exceptions import NotFoundError, DuplicateError

logger = logging.getLogger("taskverse.services.user")


class UserService:
    def __init__(self) -> None:
        StorageService._ensure_file()

    def create_user(self, user_input: UserCreateInput) -> User:
        data = StorageService.load()

        if any(u["email"] == user_input.email for u in data["users"]):
            raise DuplicateError("Email", user_input.email)

        new_user = User(**user_input.model_dump())
        data["users"].append(new_user.model_dump())
        StorageService.save(data)
        logger.info("Created user %s (%s)", new_user.name, new_user.id)
        return new_user

    def get_all_users(self) -> List[User]:
        data = StorageService.load()
        return [User(**user) for user in data["users"]]

    def get_user_by_id(self, user_id: UUID) -> User:
        data = StorageService.load()
        for user in data["users"]:
            if user["id"] == str(user_id):
                return User(**user)
        raise NotFoundError("User", str(user_id))

    def update_user(self, user_id: UUID, user_input: UserUpdateInput) -> User:
        data = StorageService.load()

        for user in data["users"]:
            if user["id"] == str(user_id):
                updates = user_input.model_dump(exclude_unset=True)

                # Check for duplicate email if email is being changed
                if "email" in updates:
                    if any(
                        u["email"] == updates["email"] and u["id"] != str(user_id)
                        for u in data["users"]
                    ):
                        raise DuplicateError("Email", updates["email"])

                for key, value in updates.items():
                    user[key] = value

                StorageService.save(data)
                logger.info("Updated user %s", user_id)
                return User(**user)

        raise NotFoundError("User", str(user_id))

    def delete_user(self, user_id: UUID) -> bool:
        data = StorageService.load()
        users = data["users"]
        for i, user in enumerate(users):
            if user["id"] == str(user_id):
                # Cascade delete: remove all tasks belonging to this user
                data["tasks"] = [
                    t for t in data["tasks"] if t["user_id"] != str(user_id)
                ]
                del users[i]
                StorageService.save(data)
                logger.info("Deleted user %s and their tasks", user_id)
                return True
        raise NotFoundError("User", str(user_id))