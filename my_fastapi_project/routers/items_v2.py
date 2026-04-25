# =============================================================================
# CHAPTER 3: Proper Error Handling and Query Parameters
# =============================================================================
#
# In Chapter 2 we returned errors like this:
#   return {"error": "Item not found"}
#
# That is wrong. The HTTP status code stays 200 OK even when something fails.
# Clients (frontend apps, mobile apps) read the status code, not the body,
# to decide whether a request succeeded or failed.
#
# This chapter fixes that and introduces two new concepts:
#
#   1. HTTPException   - raise proper HTTP errors with the correct status code
#   2. Query Parameters - accept optional filters in the URL (?skip=0&limit=10)
#
# Compare this file side by side with routers/items.py (Chapter 2) to see
# exactly what changed and why.
# =============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional


# prefix="/v2/items" avoids clashing with the Chapter 2 router (prefix="/items")
# when both are mounted in main.py at the same time.
router = APIRouter(prefix="/v2/items", tags=["items-v2"])


fake_db: dict = {
    1: {"name": "Laptop", "price": 999.99},
    2: {"name": "Phone", "price": 599.99},
    3: {"name": "Tablet", "price": 449.99},
}


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str
    price: float


class ItemPatch(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None


# =============================================================================
# CONCEPT 1: Query Parameters
# =============================================================================
# Query parameters are the key=value pairs after the ? in a URL.
#
# FastAPI detects them automatically from the function signature.
# Any argument that is NOT a path parameter becomes a query parameter.
# If the caller does not send them, the default values kick in.
#
# `skip`  -> how many items to skip (used for pagination)
# `limit` -> max number of items to return
#
# Try these in /docs:
#   GET /v2/items/                  -> all 3 items (default: skip=0, limit=10)
#   GET /v2/items/?limit=2          -> first 2 items
#   GET /v2/items/?skip=1&limit=1   -> skip 1, return 1 item
@router.get("/")
async def get_all_items(skip: int = 0, limit: int = 10):
    items = list(fake_db.items())
    return dict(items[skip : skip + limit])


# =============================================================================
# CONCEPT 2: HTTPException
# =============================================================================
# When a resource does not exist, we must return HTTP 404 Not Found.
#
# Chapter 2 way (wrong):
#   return {"error": "Item not found"}
#   -> HTTP status is still 200 OK. The client thinks it succeeded.
#
# Chapter 3 way (correct):
#   raise HTTPException(status_code=404, detail="Item not found")
#   -> HTTP status is 404. The client knows it failed.
#   -> Response body: {"detail": "Item not found"}
#   -> `raise` stops the function immediately, just like any Python exception.
#
# Rule: always raise HTTPException instead of returning error dicts.
@router.get("/{item_id}")
async def get_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


# POST: create a new item
# No change from Chapter 2 here since create never needs a 404.
@router.post("/", status_code=201)
async def create_item(item: ItemCreate):
    new_id = max(fake_db.keys()) + 1
    fake_db[new_id] = {
        "name": item.name,
        "price": item.price,
    }
    return {"id": new_id, "item": fake_db[new_id]}


# PUT: fully replace an item
# HTTPException used here instead of returning an error dict.
@router.put("/{item_id}")
async def update_item(item_id: int, item: ItemUpdate):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")

    fake_db[item_id] = {
        "name": item.name,
        "price": item.price,
    }
    return {"id": item_id, "item": fake_db[item_id]}


# PATCH: partially update an item
# HTTPException used here instead of returning an error dict.
@router.patch("/{item_id}")
async def patch_item(item_id: int, item: ItemPatch):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_item = fake_db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    updated_item = {**existing_item, **update_data}
    fake_db[item_id] = updated_item

    return {"id": item_id, "item": fake_db[item_id]}


# DELETE: remove an item
# HTTPException used here instead of returning an error dict.
@router.delete("/{item_id}")
async def delete_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = fake_db.pop(item_id)
    return {"message": f"Item '{deleted_item['name']}' deleted successfully"}
