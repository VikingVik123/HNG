# Gender Classification API

Multiple implementations of a REST endpoint that integrates with the Genderize API to classify names by gender with confidence scoring.

## Implementations

- **task.py** - FastAPI
- **task_ex.js** - Express.js
- **task_nest.js** - NestJS

## Features

- **Single GET Endpoint**: `GET /api/classify?name={name}`
- **Confidence Logic**: Returns confidence score based on probability and sample size thresholds
- **CORS Support**: Enabled for all origins to support cross-origin requests
- **Error Handling**: Comprehensive validation and error responses
- **Edge Case Handling**: Handles null gender and zero count responses
- **ISO 8601 Timestamps**: UTC timestamps in ISO 8601 format for all responses
- **Swagger/OpenAPI Documentation**: Interactive API docs available at `/api-docs`

## Setup Instructions

### 1. Install Dependencies

#### For Python (FastAPI)
```bash
pip install -r requirements.txt
```

#### For Node.js (Express/NestJS)
```bash
npm install
```

### 2. Run the Server

#### FastAPI
```bash
python task.py
```
Swagger Docs: `http://localhost:8000/api-docs` (if using FastAPI documentation)

#### Express.js
```bash
npm start
```
**Swagger Docs:** `http://localhost:8000/api-docs`

#### NestJS
```bash
npm start:nest
```
**Swagger Docs:** `http://localhost:8000/api-docs`

The servers will start on `http://localhost:8000`

## API Documentation

### Endpoint: Classify Name

**Request:**
```
GET /api/classify?name={name}
```

**Query Parameters:**
- `name` (required): The name to classify (must be a non-empty string)

**Success Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 1234,
    "is_confident": true,
    "processed_at": "2026-04-12T14:30:45Z"
  }
}
```

**Error Responses:**

1. **400 Bad Request** - Missing or empty name:
```json
{
  "status": "error",
  "message": "Missing or empty name parameter"
}
```

2. **422 Unprocessable Entity** - Name is not a string:
```json
{
  "status": "error",
  "message": "name is not a string"
}
```

3. **200 OK with error** - No prediction available:
```json
{
  "status": "error",
  "message": "No prediction available for the provided name"
}
```

4. **502 Bad Gateway** - Upstream API failure:
```json
{
  "status": "error",
  "message": "Failed to reach external API"
}
```

5. **504 Gateway Timeout** - API timeout:
```json
{
  "status": "error",
  "message": "Request to external API timed out"
}
```

6. **500 Internal Server Error** - Server error:
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

## Processing Rules

### Data Extraction
- Extracts `gender`, `probability`, and `count` from Genderize API
- Renames `count` to `sample_size` in the response
- Returns name in lowercase

### Confidence Logic
`is_confident` is `true` only when **BOTH** conditions pass:
- `probability >= 0.7`
- `sample_size >= 100`

If either condition fails, `is_confident` is `false`.

### Timestamps
- Generated on every request using UTC timezone
- Formatted as ISO 8601 (e.g., `2026-04-12T14:30:45Z`)
- Not hardcoded

### Edge Cases
- If Genderize API returns `gender: null` or `count: 0`, return error message: "No prediction available for the provided name"

## Testing Examples

### Valid Request
```bash
curl "http://localhost:8000/api/classify?name=john"
```

### Missing Name Parameter
```bash
curl "http://localhost:8000/api/classify"
```

### Empty Name Parameter
```bash
curl "http://localhost:8000/api/classify?name="
```

### Invalid Name Type
```bash
# This would be an edge case in production with type coercion
curl "http://localhost:8000/api/classify?name=123"
```

## Performance Specifications

- Response time: < 500ms (excluding external API latency)
- Handles multiple concurrent requests
- CORS headers: `Access-Control-Allow-Origin: *`

## Technical Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **External API**: Genderize.io
- **Language**: Python 3.x

## Implementation Details

### CORS Configuration
CORS middleware is configured to allow all origins, methods, and headers for maximum compatibility with external clients and grading scripts.

### Error Handling Strategy
- Uses FastAPI's HTTPException for validation errors (400, 422)
- Returns JSONResponse for API-level errors (500, 502, 504)
- Wraps Genderize API calls with timeout and exception handling

### Timeout Management
- External API request timeout: 5 seconds
- Prevents server from hanging on slow upstream responses

## Health Check

**Endpoint:**
```
GET /
```

**Response:**
```json
{
  "status": "ok",
  "message": "Gender Classification API is running"
}
```

## Deployment

This application can be deployed to:
- Vercel (with serverless function handler)
- Railway
- Heroku
- AWS (Lambda, EC2, ECS)
- PXXL App
- Any platform supporting Python/ASGI applications

## Notes

- All timestamps are in UTC
- Query parameters are case-sensitive
- Names are normalized to lowercase in the response
- The API respects Genderize's rate limits (default: 1000 requests/day for free tier)
