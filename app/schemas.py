# app/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """
    Схема входа для создания пользователя.
    """
    name: str = Field(..., min_length=1, max_length=100)
    surname: str = Field(..., min_length=1, max_length=100)


class UserRead(BaseModel):
    id: int
    name: str
    surname: str

    
    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    """
    Схема входа для создания задачи.
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10_000)
    user_id: int = Field(..., ge=1, description="ID владельца задачи")


class TaskUpdate(BaseModel):
    """
    Частичное обновление задачи: можно прислать любой из полей.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10_000)
    user_id: Optional[int] = Field(None, ge=1)

class TaskRead(BaseModel):
    """Ответ без данных о пользователе (для GET /tasks/{id})."""
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskReadWithUser(BaseModel):
    """Ответ с полями user_name и user_surname (POST/GET /tasks, /tasks/all, PUT/PATCH)."""
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    user_name: str
    user_surname: str