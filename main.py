# =============================================================================
# CHAPTER 1: Getting Started with FastAPI
# =============================================================================
#
# FastAPI is a modern, high-performance Python web framework for building APIs.
# It is built on top of Starlette (web layer) and Pydantic (data validation).
# It auto-generates interactive docs at /docs (Swagger UI).
#
# Key benefits:
#   - Very fast (on par with Node.js and Go)
#   - Automatic request validation via Pydantic
#   - Auto-generated Swagger UI at /docs
#   - Fully async-ready using Python's async/await
#
# How to run:
#   uvicorn main:app --reload
#
#   "main"     -> this file (main.py)
#   "app"      -> the FastAPI instance created below
#   "--reload" -> auto-restarts on code changes (development only)
#
# After running, visit:
#   http://127.0.0.1:8000       -> root endpoint
#   http://127.0.0.1:8000/docs  -> interactive Swagger UI (all chapters visible here)
#
# Course structure:
#   Chapter 1 -> main.py               (app setup, basic routes, mounting routers)
#   Chapter 2 -> routers/items.py      (CRUD, Pydantic models, path parameters)
#   Chapter 3 -> routers/items_v2.py   (HTTPException, query parameters)
#   Chapter 4 -> routers/items_v3.py   (real database, SQLModel, Depends)
#   Chapter 5 -> routers/items_v4.py   (response models, filtering output data)
# =============================================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI

from my_fastapi_project.routers.items import router as items_router        # Chapter 2
from my_fastapi_project.routers.items_v2 import router as items_v2_router  # Chapter 3
from my_fastapi_project.routers.items_v3 import router as items_v3_router  # Chapter 4
from my_fastapi_project.routers.items_v4 import router as items_v4_router  # Chapter 5
from my_fastapi_project.database import create_db_and_tables


# -----------------------------------------------------------------------------
# Lifespan: code that runs when the server starts and stops
# -----------------------------------------------------------------------------
# `lifespan` is the modern FastAPI way to run startup logic.
# Everything before `yield` runs when the server boots up.
# Everything after `yield` runs when the server shuts down.
#
# We call create_db_and_tables() here so the database file and the
# "item" table are created automatically before any request comes in.
@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()
    yield


# -----------------------------------------------------------------------------
# Step 1: Create the FastAPI application instance
# -----------------------------------------------------------------------------
# `lifespan=lifespan` wires up the startup/shutdown logic defined above.
app = FastAPI(
    title="FastAPI Learning Course",
    description="A beginner-friendly project covering CRUD, Pydantic models, Routers, and real databases.",
    version="1.0.0",
    lifespan=lifespan,
)


# -----------------------------------------------------------------------------
# Step 2: Root and health check routes
# -----------------------------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Health check: used by deployment platforms to verify the service is alive.
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# -----------------------------------------------------------------------------
# Step 3: Mount all chapter routers
# -----------------------------------------------------------------------------
# Chapter 2: prefix="/items"   -> basic CRUD with Pydantic and a fake dict DB
app.include_router(items_router)

# Chapter 3: prefix="/v2/items" -> same CRUD upgraded with HTTPException and query params
app.include_router(items_v2_router)

# Chapter 4: prefix="/v3/items" -> real SQLite database, SQLModel, Depends()
app.include_router(items_v3_router)

# Chapter 5: prefix="/v4/items" -> response models
app.include_router(items_v4_router)
