import asyncio
from contextlib import asynccontextmanager
import httpx
from sqlalchemy.dialects.postgresql import insert
from database import AsyncSessionLocal, Base, engine
from models import Item
from datetime import datetime, timezone

URL = "https://api.skinport.com/v1/items"
PARAMS = {"app_id": 730, "currency": "PLN", "tradable": True}
HEADERS = {"Accept-Encoding": "br"}
REFRESH_INTERVAL_SECONDS = 300



async def fetch_items() -> list[dict]:
     async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
        response = await client.get(URL, params=PARAMS)

        response.raise_for_status()

        print("status:", response.status_code)
        print("url:", response.url)
        print("content-encoding:", response.headers.get("content-encoding"))
        print("czas:", response.elapsed)

        return response.json()


async def save_items_to_db(raw_items: list[dict]) -> None:
    if not raw_items:
        return

    unique_items: dict[tuple[str, str | None], dict] = {}

    for skin in raw_items:
        hash_name = skin.get("market_hash_name")
        if not hash_name:
            continue

        version = skin.get("version")

        raw_min = skin.get("min_price")
        raw_max = skin.get("max_price")
        min_price = raw_min if raw_min is not None else (raw_max if raw_max is not None else 0.0)
        max_price = raw_max if raw_max is not None else (raw_min if raw_min is not None else 0.0)

        # Konwersja Unix timestamp ze Skinportu na obiekt datetime
        created_ts = skin.get("created_at")
        updated_ts = skin.get("updated_at")

        unique_items[(hash_name, version)] = {
            "market_hash_name": hash_name,
            "version": version,
            "currency": skin.get("currency", "PLN"),
            "suggested_price": skin.get("suggested_price"),
            "min_price": min_price,
            "max_price": max_price,
            "mean_price": skin.get("mean_price"),
            "median_price": skin.get("median_price"),
            "quantity": skin.get("quantity", 0),
            "item_page": skin.get("item_page"),
            "market_page": skin.get("market_page"),
            "source_created_at": datetime.fromtimestamp(created_ts, tz=timezone.utc) if created_ts else None,
            "source_updated_at": datetime.fromtimestamp(updated_ts, tz=timezone.utc) if updated_ts else None,
        }

    rows = list(unique_items.values())

    async with AsyncSessionLocal() as session:
        chunk_size = 1000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]

            stmt = insert(Item).values(chunk)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_item_name_version",
                set_={
                    "currency": stmt.excluded.currency,
                    "suggested_price": stmt.excluded.suggested_price,
                    "min_price": stmt.excluded.min_price,
                    "max_price": stmt.excluded.max_price,
                    "mean_price": stmt.excluded.mean_price,
                    "median_price": stmt.excluded.median_price,
                    "quantity": stmt.excluded.quantity,
                    "item_page": stmt.excluded.item_page,
                    "market_page": stmt.excluded.market_page,
                    "source_updated_at": stmt.excluded.source_updated_at,
                },
            )
            await session.execute(stmt)

        await session.commit()


async def sync_loop() -> None:
    while True:
        try:
            print("[Sync] Rozpoczynam pobieranie danych ze Skinport...")
            items = await fetch_items()
            print(f"[Sync] Sukces! Pobrano {len(items)} przedmiotów.")

            await save_items_to_db(items)
            print("[Sync] Zapis do bazy zakończony sukcesem!")

        except httpx.HTTPStatusError as e:
            print(f"[Sync] Błąd HTTP ze Skinport: {e.response.status_code}")
        except Exception as e:
            print(f"[Sync] Nieoczekiwany błąd podczas synchronizacji: {e}")

        await asyncio.sleep(REFRESH_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app):
    # tworzenie tabeli jeśli jeszcze nie istnieje
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sync_task = asyncio.create_task(sync_loop())
    print("[Lifespan] Zadanie synchronizacji w tle zostało uruchomione.")

    yield

    sync_task.cancel()
    print("[Lifespan] Zatrzymano zadanie synchronizacji w tle.")

