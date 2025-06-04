from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import secrets
import logging

from . import models, schemas, crud
from .database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create tables: {str(e)}")
    raise

app = FastAPI()

basic_auth = HTTPBasic()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(credentials: HTTPBasicCredentials = Depends(basic_auth)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/api/shorten", response_model=schemas.LinkOut)
async def create_short_link(
    link: schemas.LinkCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    try:
        logger.info(f"Creating short link for URL: {link.original_url[:50]}...")
        db_link = crud.create_short_link(db, link)
        if not db_link:
            raise HTTPException(status_code=500, detail="Failed to create link")
        return db_link
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating short link: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/links", response_model=List[schemas.LinkOut])
async def read_links(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user),
    active: Optional[bool] = None,
    limit: int = Query(default=10, le=100),
    offset: int = 0
):
    return crud.get_links(db, active=active, limit=limit, offset=offset)

@app.post("/api/deactivate/{short_code}")
async def deactivate_link(
    short_code: str,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    return crud.deactivate_link(db, short_code)

@app.get("/api/statistics", response_model=List[schemas.LinkStats])
async def get_statistics(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    return crud.get_link_statistics(db)

@app.get("/{short_code}")
async def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    link = crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    if not link.is_active:
        raise HTTPException(status_code=410, detail="Link is deactivated")
    if datetime.utcnow() > link.expires_at:
        raise HTTPException(status_code=410, detail="Link has expired")
    link.clicks += 1
    db.commit()
    return RedirectResponse(link.original_url)