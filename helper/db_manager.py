from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import Base, Creator, ActivePromo

class DatabaseManager:
    """
    Handles persistence logic, fitness updates, and cleanup.
    """

    def __init__(self, db_url: str = "postgresql://user:password@localhost:5432/promoscout"):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def upsert_promotion(self, video_data: dict, promo_data: dict):
        """
        Saves the coupon and updates the creator's intelligence trace.
        """
        with self.Session() as session:
            # 1. Update or Create Creator
            creator = session.get(Creator, video_data['channel_id'])
            if not creator:
                creator = Creator(
                    channel_id=video_data['channel_id'],
                    channel_name=video_data['channel_name']
                )
                session.add(creator)
            
            # Update intelligence metrics
            creator.fitness_score += 0.5  # Increment score for successful detection
            creator.last_detected_at = datetime.utcnow()

            # 2. Add Active Promo
            new_promo = ActivePromo(
                video_id=video_data['video_id'],
                channel_id=creator.channel_id,
                title=video_data['title'],
                upload_date=datetime.utcnow(), # Should be mapped from metadata
                brand_name=promo_data.get('brand'),
                promo_code=promo_data.get('code'),
                discount_details=promo_data.get('discount'),
                raw_extraction=promo_data
            )
            session.merge(new_promo) # Merge handles conflict if video_id exists
            
            session.commit()

    def perform_cleanup(self):
        """
        Deletes expired coupons (older than 48h) while keeping the creator history.
        """
        with self.Session() as session:
            stmt = delete(ActivePromo).where(ActivePromo.expires_at < datetime.utcnow())
            session.execute(stmt)
            session.commit()