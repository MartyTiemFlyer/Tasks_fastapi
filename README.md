# Tasks FastAPI (Quniq Test)

Асинхронный API на **FastAPI + SQLAlchemy 2.0 (Async)**.  
Реализованы CRUD по **users** и **tasks** согласно ТЗ.

## Стек
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- SQLite (для локального запуска)
- Pydantic v2
- 
Документация: http://127.0.0.1:8000/docs

## Быстрый старт

### 1) Клонирование и окружение
```bash
git clone https://github.com/MartyTiemFlyer/Tasks_fastapi.git
cd Tasks_fastapi

# (опционально) создать venv
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 1) Запуск
```bash
uvicorn app.main:app --reload
```

