from fastapi import FastAPI
from app.database.db import init_db
from app.routes import country_routes, status_route

app = FastAPI(title="Country Currency & Exchange API")

init_db()

app.include_router(country_routes.router)
app.include_router(status_route.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Country Currency & Exchange API"}
