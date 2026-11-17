import json
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from search_skins import fetch_items

from typing import Annotated

# Tworzy tabele w bazie (jeśli nie istnieją)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CS2 Market API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "CS2 Market API działa!"}


# Endpoint z bazy danych
@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(models.Item).all()
    return items


# Endpoint do synchronizacji ze Skinport → baza
@app.post("/sync-skinport")
def sync_skinport(db: Session = Depends(get_db)):
    try:
        data = fetch_items()

        added = 0
        for skin in data[:100]:  # ograniczamy do 100 dla testów
            market_hash_name = skin.get("market_hash_name")
            if not market_hash_name:
                continue

            # Sprawdź, czy już istnieje
            existing = (
                db.query(models.Item)
                .filter(models.Item.market_hash_name == market_hash_name)
                .first()
            )

            if existing:
                continue

            new_item = models.Item(
                name=market_hash_name,
                market_hash_name=market_hash_name,
                price=skin.get("suggested_price") or skin.get("min_price") or 0.0,
                min_price=skin.get("min_price"),
                max_price=skin.get("max_price"),
                suggested_price=skin.get("suggested_price"),
                quantity=skin.get("quantity", 0),
                currency=skin.get("currency", "PLN"),
                item_page=skin.get("item_page"),
            )
            db.add(new_item)
            added += 1

        db.commit()
        return {"message": f"Dodano {added} nowych skinów ze Skinport"}

    except Exception as e:
        return {"error": str(e)}


# Stary endpoint (zostawiamy na razie)
@app.get("/skins")
def show_skins():
    from search_skins import CACHE_FILE

    if CACHE_FILE.exists():
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return data[:20]
    else:
        data = fetch_items()
        return data[:20]

#Endpoint do podstrony dla danego przedmiotu
@app.get("/items/{item_id}")
def get_item(item_id: int, db: Annotated[Session, Depends(get_db)]):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        return {"error": "Nie znaleziono skina"}
    return item