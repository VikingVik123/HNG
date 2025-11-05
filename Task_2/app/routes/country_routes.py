from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database.db import get_session
from app.models.country import Country
from app.schemas.country_schema import CountryRead
from app.services.country_service import refresh_countries
from typing import List, Optional
from fastapi.responses import FileResponse, JSONResponse
from app.services.image_service import CACHE_IMAGE_PATH, generate_summary_image
import os

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("/image")
def get_summary_image():
    from fastapi.responses import FileResponse, JSONResponse
    import os
    from app.services.image_service import CACHE_IMAGE_PATH

    if not os.path.exists(CACHE_IMAGE_PATH):
        return JSONResponse(status_code=404, content={"error": "Summary image not found"})
    return FileResponse(CACHE_IMAGE_PATH, media_type="image/png")

@router.post("/refresh")
def refresh(session: Session = Depends(get_session)):
    try:
        total = refresh_countries(session)
        generate_summary_image()  # ✅ Generate summary image here
        return {"message": "Data refreshed", "total_countries": total}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/", response_model=List[CountryRead])
def get_countries(
    region: Optional[str] = None,
    currency: Optional[str] = None,
    sort: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Country)
    if region:
        query = query.where(Country.region == region)
    if currency:
        query = query.where(Country.currency_code == currency)
    if sort == "gdp_desc":
        query = query.order_by(Country.estimated_gdp.desc())
    return session.exec(query).all()

@router.get("/{name}", response_model=CountryRead)
def get_country(name: str, session: Session = Depends(get_session)):
    country = session.exec(select(Country).where(Country.name == name)).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

@router.delete("/{name}")
def delete_country(name: str, session: Session = Depends(get_session)):
    country = session.exec(select(Country).where(Country.name == name)).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    session.delete(country)
    session.commit()
    return {"message": f"{name} deleted successfully"}

