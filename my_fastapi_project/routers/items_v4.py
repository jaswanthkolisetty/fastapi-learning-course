# =============================================================================
# CHAPTER 5: Response Models
# =============================================================================
#
# Problem we discovered in the setup exercise:
#   The API was returning secret_code to the client even though it should
#   be internal only. The response had no filter on what got sent back.
#
# In all previous chapters, FastAPI returned whatever the route function
# returned. No control, no filtering. That is a security risk.
#
# Response models solve this. You define a separate model that describes
# exactly what the API should return, and FastAPI filters everything else out.
#
# New concepts in this chapter:
#
#   1. response_model=    - tell FastAPI what shape the response must have
#   2. Separate models    - one model for internal data, one for what clients see
#   3. response_model on list routes - filter a list of objects the same way
#   4. response_model_exclude_unset - only return fields that were explicitly set
#
# Real world example: a User object has a password hash stored internally.
# You never want to return that to the client. A UserPublic response model
# strips it out automatically.
# =============================================================================

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/v4/items", tags=["items-v4"])


# =============================================================================
# CONCEPT 1: Separate models for internal data vs public response
# =============================================================================
# Rule of thumb:
#   Item        -> the full internal object (has secret_code)
#   ItemCreate  -> what the client sends when creating (no id, no secret_code)
#   ItemPublic  -> what the client receives back (no secret_code)
#
# This separation is the core pattern of response models.
# The client never even knows secret_code exists.

class Item(BaseModel):
    # Full internal model. Only used inside the server, never sent to client.
    id: Optional[int] = None
    name: str
    price: float
    secret_code: str  # internal field, must never reach the client


class ItemCreate(BaseModel):
    # What the client sends when creating an item.
    # No id (server assigns it), no secret_code (client should not set it).
    name: str
    price: float


class ItemPublic(BaseModel):
    # What the client receives back. Only safe, public fields.
    # FastAPI will filter the Item object through this model before responding.
    id: Optional[int] = None
    name: str
    price: float


# =============================================================================
# CONCEPT 2: response_model on a GET route
# =============================================================================
# `response_model=ItemPublic` does two things:
#   1. FastAPI serializes the return value through ItemPublic before sending it
#   2. Any field NOT in ItemPublic is silently dropped from the response
#
# The function still works with the full Item object internally.
# secret_code exists in the object but never appears in the response.
#
# Before (Chapter 4 - no response_model):
#   response -> {"id": 1, "name": "Laptop", "price": 999.99, "secret_code": "TOP_SECRET_123"}
#
# After (with response_model=ItemPublic):
#   response -> {"id": 1, "name": "Laptop", "price": 999.99}
@router.get("/{item_id}", response_model=ItemPublic)
async def get_item(item_id: int):
    # Internally we work with the full Item including secret_code.
    # FastAPI filters it out before sending the response.
    return Item(id=item_id, name="Laptop", price=999.99, secret_code="TOP_SECRET_123")


# =============================================================================
# CONCEPT 3: response_model on a POST route
# =============================================================================
# Input and output use different models:
#   Input  -> ItemCreate (client sends name + price only)
#   Output -> ItemPublic (client receives id + name + price)
#
# This is the standard pattern for create routes.
# The client sends less than what gets stored, and receives less than what is stored.
@router.post("/", response_model=ItemPublic, status_code=201)
async def create_item(item: ItemCreate):
    # In a real app this would be saved to a database and get a real id.
    # We simulate that here by building a full Item with a fake id and secret_code.
    new_item = Item(
        id=1,
        name=item.name,
        price=item.price,
        secret_code="GENERATED_INTERNALLY",
    )
    return new_item


# =============================================================================
# CONCEPT 4: response_model on a list route
# =============================================================================
# To return a filtered list, wrap the model in List[].
# FastAPI applies ItemPublic to every object in the list.
# Every secret_code in every item gets stripped before the response is sent.
@router.get("/", response_model=List[ItemPublic])
async def get_all_items():
    fake_items = [
        Item(id=1, name="Laptop", price=999.99, secret_code="SECRET_A"),
        Item(id=2, name="Phone",  price=599.99, secret_code="SECRET_B"),
        Item(id=3, name="Tablet", price=449.99, secret_code="SECRET_C"),
    ]
    # FastAPI filters each Item through ItemPublic before sending.
    # All three secret_codes are dropped from the response.
    return fake_items
