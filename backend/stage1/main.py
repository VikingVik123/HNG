from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine, get_db
from routes import router

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
app.include_router(router)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "success", "message": "Profile Intelligence Service is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
