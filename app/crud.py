from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app import models, schemas
import uuid
import logging
import traceback

logger = logging.getLogger(__name__)

def create_short_link(db: Session, link: schemas.LinkCreate):
    existing = (
        db.query(models.Link)
        .filter(
            models.Link.original_url == link.original_url,
            models.Link.is_active == True,
            models.Link.expires_at > datetime.utcnow()
        )
        .first()
    )

    if existing:
        return existing

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            db_link = models.Link(
                original_url=link.original_url,
                short_code=str(uuid.uuid4())[:8],
                is_active=True,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=1),
                clicks=0
            )
            db.add(db_link)
            db.commit()
            db.refresh(db_link)
            return db_link

        except IntegrityError as e:
            db.rollback()
            logger.warning(f"IntegrityError on attempt {attempt + 1}: {e}")
            if attempt == max_attempts - 1:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to generate unique short code after multiple attempts"
                )

        except Exception as e:
            traceback.print_exc()
            db.rollback()
            logger.error(f"Unexpected error in create_short_link: {e}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )

def get_links(db: Session, active: bool = None, limit: int = 10, offset: int = 0):
    query = db.query(models.Link)
    if active is not None:
        query = query.filter(models.Link.is_active == active)
    return query.order_by(models.Link.created_at.desc()).offset(offset).limit(limit).all()

def deactivate_link(db: Session, short_code: str):
    link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    link.is_active = False
    db.commit()
    return {"detail": f"Link '{short_code}' deactivated"}

def get_link_by_code(db: Session, short_code: str):
    return db.query(models.Link).filter(models.Link.short_code == short_code).first()

def get_link_statistics(db: Session):
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)
    one_hour_ago = now - timedelta(hours=1)

    stats = []

    links = db.query(models.Link).all()
    for link in links:
        total_clicks = link.clicks
        clicks_last_day = db.query(models.LinkClick).filter(
            models.LinkClick.link_id == link.id,
            models.LinkClick.timestamp >= one_day_ago
        ).count()
        clicks_last_hour = db.query(models.LinkClick).filter(
            models.LinkClick.link_id == link.id,
            models.LinkClick.timestamp >= one_hour_ago
        ).count()

        stats.append(schemas.LinkStats(
            short_code=link.short_code,
            total_clicks=total_clicks,
            clicks_last_day=clicks_last_day,
            clicks_last_hour=clicks_last_hour
        ))

    return stats
