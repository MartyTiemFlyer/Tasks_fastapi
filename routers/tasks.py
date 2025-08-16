from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task, User
from app.schemas import TaskCreate, TaskUpdate, TaskRead, TaskReadWithUser
from app.db import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

# ======== helpers ========

def _task_with_user_dict(task: Task, user: User) -> dict:
    """
    Преобразует ORM-объекты Task + User в плоский словарь
    с полями user_name и user_surname.
    """
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "user_name": user.name,
        "user_surname": user.surname,
    }

# ======== CRUD ========

@router.post(
    "",
    response_model=TaskReadWithUser,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу",
)
async def create_task(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Создание новой задачи.
    Вход: `title`, `description` (опц.), `user_id`.
    Ответ: поля задачи + `user_name`, `user_surname`.
    """
    owner = await session.get(User, payload.user_id)
    if not owner:
        raise HTTPException(status_code=404, detail="User not found")

    task = Task(**payload.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return TaskReadWithUser.model_validate(_task_with_user_dict(task, owner))


@router.get(
    "",
    response_model=list[TaskReadWithUser],
    summary="Список задач для пользователя",
)
async def list_tasks_for_user(
    session: AsyncSession = Depends(get_db),
    user_id: int = Query(..., ge=1, description="ID пользователя"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Получение списка задач **для конкретного пользователя**.
    """
    stmt = (
        select(Task, User)
        .join(User, Task.user_id == User.id)
        .where(Task.user_id == user_id)
        .order_by(Task.id)
        .offset(offset)
        .limit(limit)
    )
    res = await session.execute(stmt)
    rows = res.all() 
    return [TaskReadWithUser.model_validate(_task_with_user_dict(t, u)) for t, u in rows]


@router.get(
    "/all",
    response_model=list[TaskReadWithUser],
    summary="Список всех задач с пользователями",
)
async def list_all_tasks(
    session: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Получение **всех** задач с user_name и user_surname.
    """
    stmt = (
        select(Task, User)
        .join(User, Task.user_id == User.id)
        .order_by(Task.id)
        .offset(offset)
        .limit(limit)
    )
    res = await session.execute(stmt)
    rows = res.all()
    return [TaskReadWithUser.model_validate(_task_with_user_dict(t, u)) for t, u in rows]


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Получить задачу по id (без user_* полей)",
)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Возвращает одну задачу по ID. По ТЗ — **без** user_name/user_surname.
    """
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskReadWithUser,
    summary="Частично обновить задачу",
)
@router.put(
    "/{task_id}",
    response_model=TaskReadWithUser,
    summary="Полностью обновить задачу",
)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_db),
):
    """
    Обновление задачи. Возвращает плоский ответ с user_*.
    """
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data = payload.model_dump(exclude_unset=True)

    if "user_id" in data:
        new_owner = await session.get(User, data["user_id"])
        if not new_owner:
            raise HTTPException(status_code=404, detail="User not found")

    for field, value in data.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)
    owner = await session.get(User, task.user_id)
    return TaskReadWithUser.model_validate(_task_with_user_dict(task, owner))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить задачу",
)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Удаляет задачу и возвращает сообщение об успехе.
    """
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()
    return {"detail": "Task deleted"}
