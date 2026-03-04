"""
Custom domain exceptions for TaskVerse.
Service layers raise these; route layers convert them to HTTPException.
"""


class TaskVerseError(Exception):
    """Base exception for all TaskVerse domain errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(TaskVerseError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with id '{resource_id}' not found",
            status_code=404,
        )


class DuplicateError(TaskVerseError):
    """Raised when a unique constraint is violated."""

    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"{field} '{value}' is already registered",
            status_code=400,
        )
