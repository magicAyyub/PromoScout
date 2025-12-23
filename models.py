from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Creator(Base):
    """
    Permanent table for sponsorship intelligence.
    Stores the fitness score and history of each channel.
    """
    __tablename__ = "creators"

    channel_id: Mapped[str] = mapped_column(String, primary_key=True)
    channel_name: Mapped[str] = mapped_column(String, nullable=False)
    country_code: Mapped[Optional[str]] = mapped_column(String(2))
    fitness_score: Mapped[float] = mapped_column(Float, default=1.0)
    last_detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationship to active promotions
    promotions: Mapped[List["ActivePromo"]] = relationship(back_populates="creator")

class ActivePromo(Base):
    """
    Temporary table for active coupons (TTL: 48 hours).
    Entries are meant to be searched and then deleted.
    """
    __tablename__ = "active_promos"

    video_id: Mapped[str] = mapped_column(String, primary_key=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("creators.channel_id"))
    title: Mapped[str] = mapped_column(String)
    upload_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    brand_name: Mapped[Optional[str]] = mapped_column(String)
    promo_code: Mapped[Optional[str]] = mapped_column(String)
    discount_details: Mapped[Optional[str]] = mapped_column(String)
    raw_extraction: Mapped[Optional[dict]] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.utcnow() + timedelta(days=2)
    )

    creator: Mapped["Creator"] = relationship(back_populates="promotions")