import requests
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware to explicitly set CORS header
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.get("/api/classify")
async def classify_name(name: Optional[str] = Query(None)):
    """
    Classify a name's gender using the Genderize API.
    
    Query Parameters:
        name: The name to classify (required, non-empty string)
    
    Returns:
        JSON response with classification result or error
    """
    
    # Validate name parameter - check if missing or empty
    if name is None or name == "":
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing or empty name parameter"},
        )
    
    # Validate name is a string type
    if not isinstance(name, str):
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "name is not a string"},
        )
    
    try:
        # Call Genderize API
        genderize_url = f"https://api.genderize.io/?name={name}"
        response = requests.get(genderize_url, timeout=5)
        response.raise_for_status()
        api_data = response.json()
        
        # Extract data from API response
        gender = api_data.get("gender")
        probability = api_data.get("probability")
        count = api_data.get("count")
        
        # Handle edge case: null gender or count = 0
        if gender is None or count == 0:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "error",
                    "message": "No prediction available for the provided name",
                },
            )
        
        # Compute is_confident: true when probability >= 0.7 AND sample_size >= 100
        is_confident = probability >= 0.7 and count >= 100
        
        # Generate processed_at timestamp (UTC, ISO 8601)
        processed_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Return successful response
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": {
                    "name": name.lower(),
                    "gender": gender,
                    "probability": probability,
                    "sample_size": count,
                    "is_confident": is_confident,
                    "processed_at": processed_at,
                },
            },
        )
    
    except requests.exceptions.Timeout:
        return JSONResponse(
            status_code=504,
            content={
                "status": "error",
                "message": "Request to external API timed out",
            },
        )
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            status_code=502,
            content={
                "status": "error",
                "message": "Failed to reach external API",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
            },
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Gender Classification API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
