from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User            
from app.schemas import UserCreate, UserRead
from app.db import get_db   

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Создание нового пользователя.
    Принимает JSON с `name` и `surname`, сохраняет запись в БД
    и возвращает созданного пользователя с его `id`.
    """
    
    user = User(**payload.model_dump())
    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


@router.get(
    "",
    response_model=list[UserRead],
    summary="Список пользователей (limit/offset)",
)
async def list_users(
    session: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200, description="Макс. количество пользователей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
):
    """
    Получение списка пользователей с пагинацией.
    Параметры:
    - **limit**: сколько записей вернуть (по умолчанию 50, максимум 200)  
    - **offset**: сдвиг от начала выборки (по умолчанию 0)
    Возвращает массив пользователей.
    """
    stmt = select(User).order_by(User.id).offset(offset).limit(limit)
    res = await session.execute(stmt)

    return res.scalars().all()


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Получить пользователя по id",
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Получение одного пользователя по его ID.
    Если пользователь не найден — возвращает 404.
    """
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

