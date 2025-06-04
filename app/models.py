from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime, timedelta
import uuid
from .database import Base

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(5000), nullable=False)
    short_code = Column(String(10), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)

    def __init__(self, **kwargs):
        if 'short_code' not in kwargs:
            kwargs['short_code'] = str(uuid.uuid4())[:8]
        super().__init__(**kwargs)