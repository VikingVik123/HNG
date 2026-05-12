import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.badges import router as badge_router
from app.db.base import Base
from app.db.session import engine

app = FastAPI()

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(badge_router)

# create badges directory if it doesn't exist
os.makedirs("badges", exist_ok=True)

# serve local badge files
app.mount("/badges", StaticFiles(directory="badges"), name="badges")