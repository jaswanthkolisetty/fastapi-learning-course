# FastAPI Learning Course: Zero to CRUD

A beginner-friendly FastAPI project that teaches you how to build a REST API step by step.
Every concept is explained with inline comments directly in the code. Read the source files like a textbook.

---

## What You Will Learn

| Chapter | File | Topics |
|---------|------|--------|
| 1 | `main.py` | FastAPI setup, basic routes, async functions, including routers |
| 2 | `routers/items.py` | APIRouter, Pydantic models, CRUD operations, path parameters, status codes, partial updates |

---

## Project Structure

```
Fastapi_learn/
├── main.py                      # Chapter 1: app entry point
├── requirements.txt             # project dependencies
├── README.md
└── my_fastapi_project/
    ├── __init__.py
    └── routers/
        ├── __init__.py
        └── items.py             # Chapter 2: full CRUD router
```

---

## Getting Started

**1. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the dev server**

```bash
uvicorn main:app --reload
```

**4. Open the interactive docs**

```
http://127.0.0.1:8000/docs    # Swagger UI, test endpoints in the browser
http://127.0.0.1:8000/redoc   # ReDoc, clean readable docs
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root hello world |
| GET | `/health` | Health check |
| GET | `/items/` | List all items |
| GET | `/items/{id}` | Get one item by ID |
| POST | `/items/` | Create a new item |
| PUT | `/items/{id}` | Fully replace an item |
| PATCH | `/items/{id}` | Partially update an item |
| DELETE | `/items/{id}` | Delete an item |

---

## Key Concepts

**Pydantic: automatic request validation**

```python
class ItemCreate(BaseModel):
    name: str
    price: float
```

FastAPI reads the JSON body, validates types, and returns a `422` error automatically if validation fails.

**PUT vs PATCH**

| | PUT | PATCH |
|---|---|---|
| Sends | All fields | Only changed fields |
| Missing fields | Wiped | Stay unchanged |

**Path parameters**

```python
@router.get("/{item_id}")
async def get_item(item_id: int):  # auto-cast from URL string to int
    ...
```

**Partial updates with `exclude_unset=True`**

```python
update_data = item.model_dump(exclude_unset=True)
# Only contains fields the client sent, ignores unset Optional fields
updated = {**existing, **update_data}
```

---

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) 0.135.3
- [Uvicorn](https://www.uvicorn.org/) 0.44.0
- [Pydantic](https://docs.pydantic.dev/) v2
- Python 3.10+

---

## Next Steps

- Replace the fake dict DB with SQLAlchemy or SQLModel
- Use `HTTPException` instead of returning error dicts
- Add `response_model` to control response shape
- Add query params for filtering and pagination
- Add JWT authentication
