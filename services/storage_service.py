"""
Shared JSON file storage service.
Single source of truth for all data I/O, eliminating duplication
across TaskService and UserService.
"""

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger("taskverse.storage")

# Resolve path relative to this file so it works regardless of CWD
DATA_FILE_PATH = Path(__file__).resolve().parent.parent / "storage" / "data.json"

_file_lock = Lock()


class StorageService:
    """Thread-safe JSON file storage with read/write locking."""

    @staticmethod
    def _ensure_file() -> None:
        if not DATA_FILE_PATH.exists():
            DATA_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE_PATH.write_text(json.dumps({"users": [], "tasks": []}, indent=2))
            logger.info("Created data file at %s", DATA_FILE_PATH)

    @staticmethod
    def load() -> dict[str, Any]:
        StorageService._ensure_file()
        with _file_lock:
            try:
                with open(DATA_FILE_PATH, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("Corrupted or missing data file — returning empty data")
                return {"users": [], "tasks": []}

    @staticmethod
    def save(data: dict[str, Any]) -> None:
        StorageService._ensure_file()
        with _file_lock:
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(data, f, default=str, indent=2)
            logger.debug("Data persisted to %s", DATA_FILE_PATH)
