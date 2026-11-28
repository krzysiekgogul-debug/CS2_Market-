from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func

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
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = Query(None, description="Fragment nazwy skina"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = select(models.Item).where(models.Item.quantity > 0)

    if search:
        query = query.where(models.Item.market_hash_name.ilike(f"%{search}%"))

    # Dzieki temu przedmioty beda z randomowymi cenami, a nie tylko najtansze
    query = query.order_by(func.random()).offset(offset).limit(limit)

    # Sortowanie po cenie minimalnej rosnąco
    # query = query.order_by(models.Item.min_price.asc()).offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


# Endpoint do wyszukiwania skina po nazwie lub jej fragmencie
@app.get("/items/search")
async def search_item(
    db: Annotated[AsyncSession, Depends(get_db)],
    name: str = Query(..., description="Nazwa skina lub jej fragment"),
):
    query = (
        select(models.Item)
        .where(models.Item.market_hash_name.ilike(f"%{name}%"))
        .limit(1)
    )

    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        return {"error": "Nie znaleziono skina"}

    return item


@app.get("/items/suggestions")
async def get_suggestions(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(..., min_length=2),
):
    query = (
        select(models.Item.market_hash_name)
        .where(models.Item.market_hash_name.ilike(f"%{q}%"))
        .limit(10)
    )

    result = await db.execute(query)
    names = result.scalars().all()
    return names


# Endpoint do pobierania pojedynczego skina po jego ID
@app.get("/items/{item_id}")
async def get_item(item_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Item).where(models.Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return {"error": "Nie znaleziono skina"}
    return item


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
