# =============================================================================
# CHAPTER 2: Routers, Pydantic Models, and Full CRUD
# =============================================================================
#
# This file covers the most important FastAPI concepts for building real APIs:
#
#   1. APIRouter      — splitting routes across multiple files
#   2. Pydantic       — defining and validating request/response data shapes
#   3. Path Parameters — capturing dynamic values from the URL
#   4. HTTP Methods   — GET, POST, PUT, PATCH, DELETE (full CRUD)
#   5. Status Codes   — sending the correct HTTP status in responses
#   6. Partial Updates — the difference between PUT and PATCH
#
# CRUD stands for: Create, Read, Update, Delete
# These are the four fundamental operations of any data-driven API.
# =============================================================================

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional


# =============================================================================
# CONCEPT 1: APIRouter — Modular Route Organization
# =============================================================================
# Instead of attaching all routes to the main `app`, we create a router here
# and attach it to `app` in main.py via app.include_router().
#
# Benefits:
#   - Keeps files small and focused on one resource (items, users, orders...)
#   - Easy to enable/disable entire feature groups
#   - Better team collaboration — each person owns their router
#
# `prefix="/items"` means every route in this router automatically starts with /items.
# `tags=["items"]`  groups these routes under "items" in the /docs Swagger UI.
router = APIRouter(prefix="/items", tags=["items"])


# =============================================================================
# CONCEPT 2: Fake In-Memory Database
# =============================================================================
# In a real project you'd connect to PostgreSQL, MongoDB, etc.
# For learning, we use a plain Python dictionary as a stand-in database.
# The key is the item ID (int), the value is the item data (dict).
#
# WARNING: This data resets every time you restart the server.
fake_db: dict = {
    1: {"name": "Laptop", "price": 999.99},
    2: {"name": "Phone", "price": 599.99},
    3: {"name": "Tablet", "price": 449.99},
}


# =============================================================================
# CONCEPT 3: Pydantic Models — Request Body Validation
# =============================================================================
# Pydantic models define the SHAPE of data coming into (or going out of) your API.
# When a client sends a POST/PUT/PATCH request with a JSON body, FastAPI uses
# these models to:
#   - Automatically parse the JSON into a Python object
#   - Validate that required fields are present and have the correct types
#   - Return a clear 422 error if validation fails (before your code even runs)
#
# All Pydantic models inherit from BaseModel.

class ItemCreate(BaseModel):
    """Used when CREATING a new item. Both fields are required."""
    name: str       # must be a string — FastAPI rejects the request if it's not
    price: float    # must be a number — FastAPI rejects strings like "free"


class ItemUpdate(BaseModel):
    """Used when FULLY REPLACING an item (PUT). Both fields are required."""
    name: str
    price: float


class ItemPatch(BaseModel):
    """
    Used when PARTIALLY UPDATING an item (PATCH).
    All fields are Optional — the client only sends what they want to change.
    `= None` makes each field optional with a default of None.
    """
    name: Optional[str] = None
    price: Optional[float] = None


# =============================================================================
# CONCEPT 4: READ — GET all items
# =============================================================================
# HTTP GET is used to RETRIEVE data. It should never modify anything.
# GET /items/ → returns the entire fake_db dictionary as JSON.
@router.get("/")
async def get_all_items():
    return fake_db


# =============================================================================
# CONCEPT 5: READ — GET a single item by ID (Path Parameters)
# =============================================================================
# {item_id} in the path is a "path parameter" — a dynamic segment of the URL.
# FastAPI extracts it and passes it as an argument to the function.
#
# The type hint `item_id: int` does two things:
#   1. FastAPI automatically converts the URL string to an integer
#   2. If someone passes a non-integer (e.g., /items/abc), FastAPI returns a 422 error
#
# Example: GET /items/2 → item_id = 2
@router.get("/{item_id}")
async def get_item(item_id: int):
    if item_id not in fake_db:
        # In production you'd use: raise HTTPException(status_code=404, detail="Not found")
        # We keep it simple here for learning purposes.
        return {"error": "Item not found"}
    return fake_db[item_id]


# =============================================================================
# CONCEPT 6: CREATE — POST a new item (Request Body + Status Codes)
# =============================================================================
# HTTP POST is used to CREATE a new resource.
#
# `item: ItemCreate` tells FastAPI to:
#   - Read the JSON body of the incoming request
#   - Validate it against the ItemCreate schema
#   - Inject the parsed object as `item`
#
# `status_code=201` means the response will have HTTP status 201 Created.
# The default is 200 OK. Using the correct status code is important for
# clients (mobile apps, browsers) to understand what happened.
#
# Common status codes:
#   200 OK          → success (default)
#   201 Created     → new resource was created
#   204 No Content  → success, but nothing to return (often used for DELETE)
#   400 Bad Request → client sent invalid data
#   404 Not Found   → resource doesn't exist
#   422 Unprocessable Entity → validation failed (FastAPI sends this automatically)
@router.post("/", status_code=201)
async def create_item(item: ItemCreate):
    # Generate a new ID by taking the current highest ID and adding 1.
    new_id = max(fake_db.keys()) + 1

    # Store the new item in our fake database.
    fake_db[new_id] = {
        "name": item.name,
        "price": item.price,
    }

    # Return the newly created item along with its assigned ID.
    return {"id": new_id, "item": fake_db[new_id]}


# =============================================================================
# CONCEPT 7: UPDATE (full) — PUT replaces the entire resource
# =============================================================================
# HTTP PUT is used for a FULL UPDATE — replace everything.
# The client must send ALL fields, even ones they're not changing.
#
# PUT vs PATCH:
#   PUT   → "Here is the complete new version of this resource"
#   PATCH → "Here are only the fields I want to change"
#
# This route combines a path parameter (item_id) AND a request body (item).
# FastAPI handles both at the same time — no extra setup needed.
@router.put("/{item_id}")
async def update_item(item_id: int, item: ItemUpdate):
    if item_id not in fake_db:
        return {"error": "Item not found"}

    # Completely overwrite the existing entry with the new data.
    fake_db[item_id] = {
        "name": item.name,
        "price": item.price,
    }

    return {"id": item_id, "item": fake_db[item_id]}


# =============================================================================
# CONCEPT 8: UPDATE (partial) — PATCH updates only the fields you send
# =============================================================================
# HTTP PATCH is used for a PARTIAL UPDATE — only change what's provided.
# This is more efficient than PUT when you only want to update one field.
#
# Key technique: `model.model_dump(exclude_unset=True)`
#   - model_dump()                   → returns ALL fields as a dict (including None)
#   - model_dump(exclude_unset=True) → returns ONLY fields the client actually sent
#
# Example:
#   Client sends: {"price": 799.99}
#   model_dump(exclude_unset=True) → {"price": 799.99}   ← name is excluded!
#   We then merge this with the existing data using the ** spread operator.
@router.patch("/{item_id}")
async def patch_item(item_id: int, item: ItemPatch):
    if item_id not in fake_db:
        return {"error": "Item not found"}

    existing_item = fake_db[item_id]

    # Get only the fields the client explicitly sent (ignore unset Optional fields).
    update_data = item.model_dump(exclude_unset=True)

    # Merge: start with the existing item, then overwrite with the new values.
    # {**existing_item, **update_data} → Python's dictionary spread/merge syntax.
    updated_item = {**existing_item, **update_data}
    fake_db[item_id] = updated_item

    return {"id": item_id, "item": fake_db[item_id]}


# =============================================================================
# CONCEPT 9: DELETE — Remove a resource
# =============================================================================
# HTTP DELETE is used to REMOVE a resource permanently.
# After a successful delete, many APIs return 204 No Content (nothing to return).
# We return a message here for learning clarity.
#
# `dict.pop(key)` removes the key from the dict and returns the removed value.
@router.delete("/{item_id}")
async def delete_item(item_id: int):
    if item_id not in fake_db:
        return {"error": "Item not found"}

    # pop() removes the item and returns it so we can reference it in our response.
    deleted_item = fake_db.pop(item_id)

    return {"message": f"Item '{deleted_item['name']}' deleted successfully"}
