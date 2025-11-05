from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.str import router as string_router
from app.database.db import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="String Analyzer API",
    description="An API for analyzing and managing strings with advanced filtering and natural language search.",
    version="1.0.0",
)

# Optional: Allow cross-origin requests (useful during frontend testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the string analysis router
app.include_router(string_router, tags=["String Analysis"])

# Health check route (optional but useful)
@app.get("/")
def root():
    return {"message": "String Analyzer API is running"}
