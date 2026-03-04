"""Authentication routes — register + login."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from auth import create_access_token, hash_password, verify_password, TokenResponse
from services.storage_service import StorageService
from models.user import User
from schemas.user_schemas import UserCreateInput, UserResponse
from exceptions import DuplicateError

router = APIRouter()


class LoginInput(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_input: UserCreateInput):
    """Register a new user with name, email, and password."""
    data = StorageService.load()

    if any(u["email"] == user_input.email for u in data["users"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(**user_input.model_dump(exclude={"password"}))
    user_dict = new_user.model_dump()
    user_dict["password_hash"] = hash_password(user_input.password)

    data["users"].append(user_dict)
    StorageService.save(data)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login_input: LoginInput):
    """Authenticate with email + password, returns a JWT."""
    data = StorageService.load()

    user = next(
        (u for u in data["users"] if u["email"] == login_input.email),
        None,
    )

    if not user or not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(login_input.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": user["id"]})
    return TokenResponse(access_token=token)
