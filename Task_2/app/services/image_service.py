import os
from PIL import Image, ImageDraw, ImageFont
from sqlmodel import Session, select
from sqlalchemy import func
from app.models.country import Country
from datetime import datetime
from app.database.db import engine

CACHE_DIR = "app/cache"
CACHE_IMAGE_PATH = os.path.join(CACHE_DIR, "summary.png")

def generate_summary_image():
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    with Session(engine) as session:
        total = session.exec(select(func.count()).select_from(Country)).one()
        top5 = session.exec(
            select(Country).order_by(Country.estimated_gdp.desc().nullslast()).limit(5)
        ).all()
        last_refreshed = session.exec(
            select(Country.last_refreshed_at).order_by(Country.last_refreshed_at.desc())
        ).first()
    
    last_refreshed_str = last_refreshed.isoformat() if last_refreshed else "N/A"

    # Create image
    img = Image.new("RGB", (800, 500), color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.text((20, 20), "Countries Summary", fill="black", font=font)
    draw.text((20, 60), f"Total countries: {total}", fill="black", font=font)
    draw.text((20, 90), f"Last refreshed: {last_refreshed_str}", fill="black", font=font)

    draw.text((20, 130), "Top 5 countries by Estimated GDP:", fill="black", font=font)
    y = 160
    for i, c in enumerate(top5, start=1):
        gdp = f"{c.estimated_gdp:,.2f}" if c.estimated_gdp else "N/A"
        draw.text((40, y), f"{i}. {c.name} — {gdp}", fill="black", font=font)
        y += 30

    img.save(CACHE_IMAGE_PATH)
    return CACHE_IMAGE_PATH


