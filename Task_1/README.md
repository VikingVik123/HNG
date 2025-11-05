# String Analyzer API

A small FastAPI service that analyzes, stores, filters, and manages strings. It computes properties like length, word count, palindrome detection, a SHA‑256 id/hash, and a per-character frequency map. The service persists records in a local SQLite database (`strings.db`) and exposes REST endpoints for create/read/delete and natural-language style filtering.

## Table of contents

- [Features](#features)
- [Quick start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Data model](#data-model)
- [Database](#database)
- [Examples](#examples)
  - [curl examples](#curl-examples)
  - [Python (httpx) example](#python-httpx-example)
- [Development notes](#development-notes)
- [Quality gates / troubleshooting](#quality-gates--troubleshooting)
- [Next steps](#next-steps)
- [License](#license)

## Features

- Analyze a submitted string (length, palindrome check, unique characters, word count).
- Compute SHA-256 hash for stable ID usage.
- Store string records in a local SQLite database (`strings.db`).
- Query stored records using structured query parameters or a simple natural-language filter endpoint.
- Delete string records.
- CORS enabled for easy frontend testing.

## Quick start

Requirements

- Python 3.10+ recommended
- The project includes a `requirements.txt` with dependencies used by the app.

If you prefer to use the included virtual environment, activate it first (UNIX / bash):

```bash
source env/bin/activate
```

Install dependencies (if not using the provided virtualenv):

```bash
pip install -r requirements.txt
```

Run the app with Uvicorn (from project root `Task_1`):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The app will create the SQLite database file `strings.db` in the same directory on first run.

Open the interactive docs:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

Base path: root of the server (e.g. `http://127.0.0.1:8000`).

1. POST /strings
   - Create and analyze a string. Returns analyzed properties.
   - Request body: JSON `{ "value": "your string here" }`
   - Responses:
     - 201 Created: returns `StringOut` model with `id`, `value`, `properties`, `created_at`
     - 400 Bad Request: missing/invalid value
     - 409 Conflict: string already exists

2. GET /strings/{string_value}
   - Retrieve the stored record for the exact string value.
   - Responses:
     - 200 OK: `StringOut`
     - 404 Not Found: string not stored

3. GET /strings
   - List stored strings with optional filters via query parameters.
   - Query parameters (all optional):
     - `is_palindrome` (bool)
     - `min_length` (int)
     - `max_length` (int)
     - `word_count` (int)
     - `contains_character` (string, single character)
   - Returns JSON with `data` (list of records), `count`, and `filters_applied`.

4. GET /strings/filter-by-natural-language
   - A simple natural-language interpreted filter. Provide `query` as a required parameter.
   - Examples of supported heuristics: "palindromic", "single word", "longer than 5", "containing the letter a".
   - Returns interpreted filters and matched data.

5. DELETE /strings/{string_value}
   - Deletes the stored record matching the exact `string_value`.
   - Responses:
     - 204 No Content: deleted
     - 404 Not Found: string not stored

## Data model

The app uses a SQLAlchemy model defined in `app/models/string.py`:

- `id` (string): primary key, set to the SHA-256 hash of the value
- `value` (string): original string, unique
- `length` (int)
- `is_palindrome` (bool)
- `unique_characters` (int)
- `word_count` (int)
- `sha256_hash` (string): hex digest of the value
- `character_frequency_map` (JSON): map of character -> frequency
- `created_at` (datetime)

Pydantic schemas exposed to clients are in `app/schemas/string_schema.py`:

- `StringIn` expects `{ value: str }`
- `StringOut` returns `id`, `value`, `properties` (dict), `created_at`

## Database

- SQLite database file: `strings.db` (created automatically by the app on startup).
- SQLAlchemy `engine` and `SessionLocal` are configured in `app/database/db.py`.
- Schemas/tables are created at app startup via `Base.metadata.create_all(bind=engine)` in `main.py`.

## Examples

### curl examples

Create a string:

```bash
curl -s -X POST "http://127.0.0.1:8000/strings" \
  -H "Content-Type: application/json" \
  -d '{"value": "A man a plan a canal Panama"}' | jq
```

Get a specific string (exact match required):

```bash
curl -s "http://127.0.0.1:8000/strings/A%20man%20a%20plan%20a%20canal%20Panama" | jq
```

Filter by query params:

```bash
curl -s "http://127.0.0.1:8000/strings?is_palindrome=true&min_length=3" | jq
```

Natural-language filter:

```bash
curl -s "http://127.0.0.1:8000/strings/filter-by-natural-language?query=palindromic%20single%20word" | jq
```

Delete a string:

```bash
curl -s -X DELETE "http://127.0.0.1:8000/strings/hello%20world"
```

### Python (httpx) example

```python
import httpx

url = "http://127.0.0.1:8000/strings"
with httpx.Client() as client:
    r = client.post(url, json={"value": "racecar"})
    print(r.status_code, r.json())

    r = client.get("http://127.0.0.1:8000/strings?is_palindrome=true")
    print(r.status_code, r.json())
```

## Development notes

- CORS is currently configured to allow all origins. Replace the wildcard in `main.py` with a specific origin for production.
- The API uses the plain string value as the lookup key for several endpoints (e.g. `GET /strings/{string_value}`). Values are stored verbatim, so URL encoding is required for spaces and special characters when calling those endpoints.
- The code uses a simple heuristic parser for the natural language filter. It's intentionally lightweight and limited. For more advanced parsing, integrate an NLP library or a rules engine.
- The `app/database/crud.py` contains a small class wrapper for CRUD operations; routes currently use SQLAlchemy sessions directly.

## Quality gates / troubleshooting

- Lint / type-check: your editor may show `Import ... could not be resolved` for `fastapi`, `pydantic`, or `sqlalchemy` if the Python environment used by the editor doesn't have the packages installed. Fix by activating the provided `env` virtualenv or installing the requirements:

```bash
source env/bin/activate   # if you want to use the included virtualenv
pip install -r requirements.txt
```

- Running the app requires the dependencies listed in `requirements.txt`.

- Tests: this repository does not include automated tests yet.

## Next steps (suggested)

- Add unit tests for route handlers and CRUD operations.
- Add pagination and sorting to `GET /strings`.
- Harden natural-language parsing or integrate a small rule-based or ML-based NLP component.
- Add Dockerfile and docker-compose for easy deployment.
- Add authentication/authorization (e.g., API key or OAuth2) if needed.

## Files changed/created

- `README.md` — this file: usage, endpoints, examples, and development notes.

## License

MIT-style (add your own license if desired).

---

If you'd like, I can also:

- Add basic tests and a tiny test runner using pytest.
- Add a Dockerfile and example docker-compose.
- Expand the natural-language parser to support more phrases.

Tell me which follow-up you prefer and I will implement it next.