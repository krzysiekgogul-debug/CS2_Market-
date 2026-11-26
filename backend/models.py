from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)

    # Identyfikacja skina
    market_hash_name = Column(String, index=True, nullable=False)
    version = Column(String, nullable=True)  # np. "Ruby", "Phase 2" lub None
    currency = Column(String, nullable=False, default="PLN")

    # Komplet cen ze Skinportu
    suggested_price = Column(Float, nullable=True)
    min_price = Column(Float, nullable=False, default=0.0)
    max_price = Column(Float, nullable=False, default=0.0)
    mean_price = Column(Float, nullable=True)
    median_price = Column(Float, nullable=True)

    # Dostępność i linki
    quantity = Column(Integer, nullable=False, default=0)
    item_page = Column(String, nullable=True)
    market_page = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    # Daty ze Skinportu (kiedy Skinport utworzył i zaktualizował rekord)
    source_created_at = Column(DateTime(timezone=True), nullable=True)
    source_updated_at = Column(DateTime(timezone=True), nullable=True)

    # Daty techniczne w Twojej bazie danych
    db_created_at = Column(DateTime(timezone=True), server_default=func.now())
    db_updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "market_hash_name",
            "version",
            name="uq_item_name_version",
            postgresql_nulls_not_distinct=True,
        ),
    )
