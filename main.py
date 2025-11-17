import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from database import db, create_document, get_documents

app = FastAPI(title="Riftlol Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Utils -----
class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool
    images: Optional[List[str]] = None
    rating: Optional[float] = None
    stock_qty: Optional[int] = 0
    tags: Optional[List[str]] = None
    featured: bool = False
    created_at: Optional[datetime] = None


def serialize_doc(doc: dict) -> dict:
    d = doc.copy()
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    # convert datetimes to isoformat for JSON
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


# ----- Startup: seed demo data if empty -----
@app.on_event("startup")
def seed_if_empty():
    try:
        if db is None:
            return
        count = db["product"].count_documents({})
        if count == 0:
            demo_products = [
                {
                    "title": "Stitch Plush - Classic Blue",
                    "description": "Super-soft Stitch plush, 12-inch collectible.",
                    "price": 24.99,
                    "category": "plush",
                    "in_stock": True,
                    "images": [
                        "https://images.unsplash.com/photo-1546778316-dfda79f1c5d0?q=80&w=1200&auto=format&fit=crop",
                    ],
                    "rating": 4.8,
                    "stock_qty": 120,
                    "tags": ["stitch", "plush", "disney"],
                    "featured": True,
                },
                {
                    "title": "Stitch Keychain Mini Plush",
                    "description": "Pocket-size Stitch charm for backpacks.",
                    "price": 9.99,
                    "category": "accessories",
                    "in_stock": True,
                    "images": [
                        "https://images.unsplash.com/photo-1588422333073-3f83f9b7f1a3?q=80&w=1200&auto=format&fit=crop",
                    ],
                    "rating": 4.6,
                    "stock_qty": 300,
                    "tags": ["stitch", "keychain"],
                    "featured": True,
                },
                {
                    "title": "Trading Card Booster Pack - Riftlol Edition",
                    "description": "10 cards per pack, chance of holographic rares.",
                    "price": 5.99,
                    "category": "cards",
                    "in_stock": True,
                    "images": [
                        "https://images.unsplash.com/photo-1603575449060-397ac9c3e9b3?q=80&w=1200&auto=format&fit=crop",
                    ],
                    "rating": 4.5,
                    "stock_qty": 500,
                    "tags": ["trading", "cards", "booster"],
                    "featured": True,
                },
                {
                    "title": "Collector Binder - Neon Rift",
                    "description": "Store up to 360 cards with UV-protect sleeves.",
                    "price": 19.99,
                    "category": "cards",
                    "in_stock": True,
                    "images": [
                        "https://images.unsplash.com/photo-1603570419969-23f9139abf1d?q=80&w=1200&auto=format&fit=crop",
                    ],
                    "rating": 4.7,
                    "stock_qty": 220,
                    "tags": ["binder", "cards"],
                    "featured": False,
                },
                {
                    "title": "Arcade Pixel Lamp",
                    "description": "RGB mood lamp inspired by retro arcades.",
                    "price": 29.99,
                    "category": "toys",
                    "in_stock": True,
                    "images": [
                        "https://images.unsplash.com/photo-1520975693411-b46f52b85097?q=80&w=1200&auto=format&fit=crop",
                    ],
                    "rating": 4.4,
                    "stock_qty": 80,
                    "tags": ["lamp", "gaming"],
                    "featured": False,
                },
            ]
            for p in demo_products:
                create_document("product", p)
    except Exception:
        # fail silently so app still boots even if DB not configured
        pass


# ----- Basic routes -----
@app.get("/")
def read_root():
    return {"message": "Riftlol Store API running"}


@app.get("/api/products")
def list_products(
    category: Optional[str] = Query(default=None),
    featured: Optional[bool] = Query(default=None),
    limit: int = Query(default=24, ge=1, le=100),
):
    """List products with optional filters"""
    try:
        filt = {}
        if category:
            filt["category"] = category
        if featured is not None:
            filt["featured"] = featured
        docs = get_documents("product", filt, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        # If DB unavailable, return empty list with reason
        return []


@app.get("/api/featured")
def featured_products(limit: int = Query(default=8, ge=1, le=24)):
    try:
        docs = get_documents("product", {"featured": True}, limit)
        return [serialize_doc(d) for d in docs]
    except Exception:
        return []


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
