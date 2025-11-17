"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category, e.g., toys, plush, cards")
    in_stock: bool = Field(True, description="Whether product is in stock")
    images: List[HttpUrl] | None = Field(default=None, description="Image URLs for the product")
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="Average rating 0-5")
    stock_qty: Optional[int] = Field(default=0, ge=0, description="Units available in stock")
    tags: List[str] | None = Field(default=None, description="Searchable tags")
    featured: bool = Field(default=False, description="Showcase on homepage")
