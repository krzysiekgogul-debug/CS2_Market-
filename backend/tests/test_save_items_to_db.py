import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import search_skins
from database import Base
from models import Item

# Osobna baza testowa w kontenerze PostgreSQL
TEST_DB_URL = "postgresql+asyncpg://cs2user:cs2password@localhost:15432/cs2market_test"
# towrzenie testowej bazy
# docker compose exec db psql -U cs2user -d cs2market -c "CREATE DATABASE cs2market_test;"
# pip install -r requirements-dev.txt


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL)
    TestSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # 1. Tworzymy tabele przed testem
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Podmieniamy sesję w search_skins na testową (żeby nie ruszać prawdziwej bazy!)
    original_session = search_skins.AsyncSessionLocal
    search_skins.AsyncSessionLocal = TestSessionLocal

    async with TestSessionLocal() as session:
        yield session

    # 2. Sprzątamy po teście i przywracamy oryginalną sesję
    search_skins.AsyncSessionLocal = original_session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_save_items_price_fallback_and_doppler_versions(db_session: AsyncSession):
    # ARRANGE: Surowe dane ze Skinportu
    raw_items = [
        {
            "market_hash_name": "★ Karambit | Doppler (Factory New)",
            "version": "Ruby",
            "min_price": 15000.0,
            "max_price": None,  # Brak max_price -> powinien skopiować 15000.0
            "quantity": 1,
        },
        {
            "market_hash_name": "★ Karambit | Doppler (Factory New)",
            "version": "Sapphire",
            "min_price": None,  # Brak obu cen -> powinien wstawić 0.0
            "max_price": None,
            "quantity": 0,
        },
    ]

    # ACT: Zapisujemy do bazy testowej
    await search_skins.save_items_to_db(raw_items)

    # ASSERT: Sprawdzamy zawartość tabeli
    result = await db_session.execute(select(Item).order_by(Item.version.asc()))
    items = result.scalars().all()

    assert len(items) == 2
    assert items[0].version == "Ruby"
    assert items[0].min_price == 15000.0
    assert items[0].max_price == 15000.0

    assert items[1].version == "Sapphire"
    assert items[1].min_price == 0.0
    assert items[1].max_price == 0.0


@pytest.mark.asyncio
async def test_save_items_upsert_updates_existing_record(db_session: AsyncSession):
    # ARRANGE & ACT 1: Pierwszy zapis skina
    await search_skins.save_items_to_db(
        [
            {
                "market_hash_name": "AK-47 | Redline (Field-Tested)",
                "min_price": 50.0,
                "max_price": 80.0,
                "quantity": 5,
            }
        ]
    )

    # ACT 2: Kolejna synchronizacja ze Skinportu ze zmienioną ceną i ilością
    await search_skins.save_items_to_db(
        [
            {
                "market_hash_name": "AK-47 | Redline (Field-Tested)",
                "min_price": 65.0,
                "max_price": 90.0,
                "quantity": 8,
            }
        ]
    )

    # ASSERT: W bazie dalej ma być TYLKO 1 rekord, ale ze zaktualizowanymi danymi!
    result = await db_session.execute(select(Item))
    items = result.scalars().all()

    assert len(items) == 1
    assert items[0].min_price == 65.0
    assert items[0].max_price == 90.0
    assert items[0].quantity == 8
