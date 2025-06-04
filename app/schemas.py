from pydantic import BaseModel
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: str

class LinkOut(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: datetime
    is_active: bool
    clicks: int

    class Config:
        from_attributes = True

class LinkStats(BaseModel):
    short_code: str
    clicks: int

    class Config:
        from_attributes = True