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
# =============================================================================

from fastapi import FastAPI

# Each chapter lives in its own router file.
# We import them here and mount them onto the main app below.
from my_fastapi_project.routers.items import router as items_router        # Chapter 2
from my_fastapi_project.routers.items_v2 import router as items_v2_router  # Chapter 3


# -----------------------------------------------------------------------------
# Step 1: Create the FastAPI application instance
# -----------------------------------------------------------------------------
# Think of `app` as the central hub of your entire API.
# All routes and routers attach to this object.
# The title, description, and version show up in the /docs Swagger UI page.
app = FastAPI(
    title="FastAPI Learning Course",
    description="A beginner-friendly project covering CRUD, Pydantic models, and Routers.",
    version="1.0.0",
)


# -----------------------------------------------------------------------------
# Step 2: Define your first route
# -----------------------------------------------------------------------------
# @app.get("/") is a route decorator. It tells FastAPI:
#   - Listen for HTTP GET requests at the "/" path
#   - Call this function when a request hits that path
#
# `async def` marks this as an async function.
# FastAPI supports both `def` and `async def`.
# Use `async def` when your function does any I/O (DB queries, file reads, etc.)
@app.get("/")
async def root():
    # FastAPI automatically converts the returned dict into a JSON response.
    # No json.dumps() or Content-Type headers needed.
    return {"message": "Hello World"}


# -----------------------------------------------------------------------------
# Step 3: Health check endpoint
# -----------------------------------------------------------------------------
# Health check routes are a standard pattern used by deployment platforms
# (Docker, Kubernetes, AWS ELB) to verify the service is alive and ready.
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# -----------------------------------------------------------------------------
# Step 4: Mount routers onto the main app
# -----------------------------------------------------------------------------
# Instead of writing all routes in this one file, we split them into routers.
# `include_router()` attaches all routes from a router file to the app.
# The order here determines the order they appear in /docs.

# Chapter 2 routes: prefix="/items"
#   GET    /items/      -> list all items
#   POST   /items/      -> create an item
#   GET    /items/{id}  -> get one item
#   PUT    /items/{id}  -> fully replace an item
#   PATCH  /items/{id}  -> partially update an item
#   DELETE /items/{id}  -> delete an item
app.include_router(items_router)

# Chapter 3 routes: prefix="/v2/items"
# Same CRUD routes but upgraded with:
#   - HTTPException for proper error status codes
#   - Query parameters for pagination (?skip=0&limit=10)
app.include_router(items_v2_router)
