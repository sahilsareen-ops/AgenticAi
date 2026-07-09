from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Role(str, Enum):
    admin = "admins"
    editor = "editor"
    viewer = "viewer"


class Address(BaseModel):
    street: str
    city: str
    zip_code: str = Field(pattern=r"^\d{5}$")


class User(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=50)
    email: str
    role: Role = Role.viewer
    age: Optional[int] = Field(default=None, ge=0, le=120)
    address: Optional[Address] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    @classmethod
    def name_must_be_capitalized(cls, v: str) -> str:
        return v.strip().title()


class Product(BaseModel):
    sku: str
    title: str
    price: float = Field(gt=0)
    in_stock: bool = True
    tags: list[str] = Field(default_factory=list)


class Order(BaseModel):
    order_id: int
    user: User
    products: list[Product]
    total: float = Field(gt=0)

    @field_validator("total")
    @classmethod
    def total_must_match_products(cls, v: float, info) -> float:
        products = info.data.get("products", [])
        expected = sum(p.price for p in products)
        if products and round(v, 2) != round(expected, 2):
            raise ValueError(f"total {v} does not match sum of product prices {expected}")
        return v
