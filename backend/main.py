from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from search_skins import lifespan

app = FastAPI(title="CS2 Market API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/skins_from_db")
async def get_skins_from_db(
    search: str | None = Query(None, description="Fragment nazwy skina, np. AK-47"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(models.Item).where(models.Item.quantity > 0)

    if search:
        query = query.where(models.Item.market_hash_name.ilike(f"%{search}%"))

    query = query.order_by(models.Item.min_price.asc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Endpoint z bazy danych
# @app.get("/items")
# def get_items(db: Session = Depends(get_db)):
#     items = db.query(models.Item).all()
#     return items
# Endpoint do synchronizacji ze Skinport → baza(synchroniczna nie będzie działać aktualnie)
# @app.post("/sync-skinport")
# def sync_skinport(db: Session = Depends(get_db)):
#     try:
#         data = fetch_items()
#
#         added = 0
#         for skin in data[:100]:  # ograniczamy do 100 dla testów
#             market_hash_name = skin.get("market_hash_name")
#             if not market_hash_name:
#                 continue
#
#             # Sprawdź, czy już istnieje
#             existing = (
#                 db.query(models.Item)
#                 .filter(models.Item.market_hash_name == market_hash_name)
#                 .first()
#             )
#
#             if existing:
#                 continue
#
#             new_item = models.Item(
#                 name=market_hash_name,
#                 market_hash_name=market_hash_name,
#                 price=skin.get("suggested_price") or skin.get("min_price") or 0.0,
#                 min_price=skin.get("min_price"),
#                 max_price=skin.get("max_price"),
#                 suggested_price=skin.get("suggested_price"),
#                 quantity=skin.get("quantity", 0),
#                 currency=skin.get("currency", "PLN"),
#                 item_page=skin.get("item_page"),
#             )
#             db.add(new_item)
#             added += 1
#
#         db.commit()
#         return {"message": f"Dodano {added} nowych skinów ze Skinport"}
#
#     except Exception as e:
#         return {"error": str(e)}
