"""API routes for the URL shortener."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.database import get_db
from app.models import ShortUrl
from app.utils import encode

router = APIRouter()


class ShortenRequestBody(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    short_id: str
    original_url: str
    clicks: int


@router.post("/api/shorten", response_model=ShortenResponse, status_code=201)
def create_short_url(body: ShortenRequestBody, db: Session = Depends(get_db)):
    """Create a short URL for the given long URL."""
    # Check if this URL was already shortened
    existing = db.query(ShortUrl).filter(ShortUrl.original_url == str(body.url)).first()
    if existing:
        return ShortenResponse(
            short_url=f"/{existing.short_id}",
            original_url=existing.original_url,
        )

    # Create new entry
    new_url = ShortUrl(original_url=str(body.url), short_id="", clicks=0)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    # Generate short_id from the auto-incremented ID
    new_url.short_id = encode(new_url.id)
    db.commit()

    return ShortenResponse(
        short_url=f"/{new_url.short_id}",
        original_url=new_url.original_url,
    )


@router.get("/api/stats/{short_id}", response_model=StatsResponse)
def get_stats(short_id: str, db: Session = Depends(get_db)):
    """Get click statistics for a short URL."""
    url_entry = db.query(ShortUrl).filter(ShortUrl.short_id == short_id).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return StatsResponse(
        short_id=url_entry.short_id,
        original_url=url_entry.original_url,
        clicks=url_entry.clicks,
    )


@router.get("/{short_id}")
def redirect_to_url(short_id: str, db: Session = Depends(get_db)):
    """Redirect a short URL to its original destination."""
    url_entry = db.query(ShortUrl).filter(ShortUrl.short_id == short_id).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Increment click counter
    url_entry.clicks += 1
    db.commit()

    return RedirectResponse(url=url_entry.original_url, status_code=302)
