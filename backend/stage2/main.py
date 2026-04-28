from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine, get_db
from routers.routes import router
from routers.auth_routes import router as auth_router
from routers.user_routes import router as user_router

# Import models to register them with Base (must be before create_all)
from models.auth_model import Token
from models.user_model import Users
from models.model import Profile

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Profile Intelligence Service",
    description="API for enriching profiles with gender, age, and nationality data",
    version="1.0.0"
)

# Add CORS middleware - Allow all origins as required
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Access-Control-Allow-Origin: *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(router)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "success", "message": "Profile Intelligence Service is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
