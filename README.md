# FastAPI Learning Course: Zero to CRUD

A beginner-friendly FastAPI project that teaches you how to build a REST API step by step.
Every concept is explained with inline comments directly in the code. Read the source files like a textbook.

---

## What You Will Learn

| Chapter | File | Topics |
|---------|------|--------|
| 1 | `main.py` | FastAPI setup, basic routes, async functions, lifespan, mounting routers |
| 2 | `routers/items.py` | APIRouter, Pydantic models, full CRUD, path parameters, status codes, partial updates |
| 3 | `routers/items_v2.py` | HTTPException, proper error status codes, query parameters, pagination |
| 4 | `routers/items_v3.py` | SQLModel, real SQLite database, Depends(), session management |
| 5 | `routers/items_v4.py` | Response models, filtering output, separate input/output schemas |

---

## Project Structure

```
Fastapi_learn/
├── main.py                          # Chapter 1: app entry point, mounts all routers
├── requirements.txt                 # project dependencies
├── README.md
└── my_fastapi_project/
    ├── __init__.py
    ├── database.py                  # Chapter 4: DB engine, session, table creation
    └── routers/
        ├── __init__.py
        ├── items.py                 # Chapter 2: full CRUD with fake dict DB
        ├── items_v2.py              # Chapter 3: HTTPException + query parameters
        ├── items_v3.py              # Chapter 4: real SQLite DB with SQLModel
        └── items_v4.py              # Chapter 5: response models, output filtering
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
http://127.0.0.1:8000/docs    # Swagger UI, test every endpoint in the browser
http://127.0.0.1:8000/redoc   # ReDoc, clean readable docs
```

---

## API Reference

**Chapter 2** - in-memory CRUD

| Method | Path | Description |
|--------|------|-------------|
| GET | `/items/` | List all items |
| GET | `/items/{id}` | Get one item by ID |
| POST | `/items/` | Create a new item |
| PUT | `/items/{id}` | Fully replace an item |
| PATCH | `/items/{id}` | Partially update an item |
| DELETE | `/items/{id}` | Delete an item |

**Chapter 3** - same CRUD, proper errors and pagination

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v2/items/?skip=0&limit=10` | List items with pagination |
| GET | `/v2/items/{id}` | Get one item, returns 404 if missing |
| POST | `/v2/items/` | Create a new item |
| PUT | `/v2/items/{id}` | Fully replace an item |
| PATCH | `/v2/items/{id}` | Partially update an item |
| DELETE | `/v2/items/{id}` | Delete an item |

**Chapter 4** - real database (data persists between restarts)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v3/items/` | List all items from SQLite |
| GET | `/v3/items/{id}` | Get one item from SQLite |
| POST | `/v3/items/` | Save a new item to SQLite |
| DELETE | `/v3/items/{id}` | Delete an item from SQLite |

---

## Key Concepts

**Pydantic: automatic request validation**

```python
class ItemCreate(BaseModel):
    name: str
    price: float
```

FastAPI reads the JSON body, validates types, and returns `422` automatically if validation fails.

**HTTPException: proper error responses**

```python
# wrong (status stays 200)
return {"error": "Item not found"}

# correct (status is 404)
raise HTTPException(status_code=404, detail="Item not found")
```

**PUT vs PATCH**

| | PUT | PATCH |
|---|---|---|
| Sends | All fields | Only changed fields |
| Missing fields | Wiped | Stay unchanged |

**Query parameters**

```python
@router.get("/")
async def get_all_items(skip: int = 0, limit: int = 10):
    # GET /items/?skip=0&limit=5
```

**SQLModel table**

```python
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
```

**Dependency injection with Depends()**

```python
@router.get("/")
async def get_items(session: Session = Depends(get_session)):
    # FastAPI injects the DB session automatically before the route runs
    return session.exec(select(Item)).all()
```

**Save a new row to the database**

```python
session.add(item)      # stage it
session.commit()       # write to DB
session.refresh(item)  # reload so auto-generated id is populated
```

**Response models: control what the client receives**

```python
class ItemPublic(BaseModel):
    id: int
    name: str
    price: float
    # secret_code is NOT here, so it never reaches the client

@router.get("/{item_id}", response_model=ItemPublic)
async def get_item(item_id: int):
    return Item(id=1, name="Laptop", price=999.99, secret_code="hidden")
    # FastAPI filters the response through ItemPublic before sending
    # secret_code is silently dropped
```

---

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) 0.135.3
- [Uvicorn](https://www.uvicorn.org/) 0.44.0
- [Pydantic](https://docs.pydantic.dev/) v2
- [SQLModel](https://sqlmodel.tiangolo.com/) 0.0.38
- SQLite (built into Python, no install needed)
- Python 3.10+

---

## What is Coming Next

- Response models (`response_model=`) to control what gets returned
- PUT update route for the real database
- Authentication with JWT tokens
- Deploying FastAPI to production
