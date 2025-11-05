import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.string import StringRecord
from app.schemas.string_schema import StringIn, StringOut
from app.database.crud import StringCRUD

router = APIRouter()


# ---------- Helper: Analyze String ----------
def analyze_string(value: str):
    cleaned = ''.join(value.lower().split())
    is_palindrome = cleaned == cleaned[::-1]
    unique_chars = len(set(value))
    word_count = len(value.split())
    sha256_hash = hashlib.sha256(value.encode()).hexdigest()
    freq_map = {}
    for ch in value:
        freq_map[ch] = freq_map.get(ch, 0) + 1
    return {
        "length": len(value),
        "is_palindrome": is_palindrome,
        "unique_characters": unique_chars,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": freq_map,
    }


# ---------- 1. Create / Analyze String ----------
@router.post("/strings", response_model=StringOut, status_code=201)
def create_string(payload: StringIn, db: Session = Depends(get_db)):
    if not payload.value or not isinstance(payload.value, str):
        raise HTTPException(status_code=400, detail="Missing or invalid 'value' field")

    props = analyze_string(payload.value)
    existing = db.query(StringRecord).filter(StringRecord.value == payload.value).first()
    if existing:
        raise HTTPException(status_code=409, detail="String already exists")

    new_record = StringRecord(
        id=props["sha256_hash"],  # use hash as ID
        value=payload.value,
        length=props["length"],
        is_palindrome=props["is_palindrome"],
        unique_characters=props["unique_characters"],
        word_count=props["word_count"],
        sha256_hash=props["sha256_hash"],
        character_frequency_map=props["character_frequency_map"],
        created_at=datetime.utcnow(),
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return StringOut(
        id=new_record.id,
        value=new_record.value,
        properties={
            "length": new_record.length,
            "is_palindrome": new_record.is_palindrome,
            "unique_characters": new_record.unique_characters,
            "word_count": new_record.word_count,
            "sha256_hash": new_record.sha256_hash,
            "character_frequency_map": new_record.character_frequency_map,
        },
        created_at=new_record.created_at,
    )


# ---------- 2. Get Specific String ----------
@router.get("/strings/{string_value}", response_model=StringOut)
def get_string(string_value: str, db: Session = Depends(get_db)):
    record = db.query(StringRecord).filter(StringRecord.value == string_value).first()
    if not record:
        raise HTTPException(status_code=404, detail="String does not exist")

    return StringOut(
        id=record.sha256_hash,
        value=record.value,
        properties={
            "length": record.length,
            "is_palindrome": record.is_palindrome,
            "unique_characters": record.unique_characters,
            "word_count": record.word_count,
            "sha256_hash": record.sha256_hash,
            "character_frequency_map": record.character_frequency_map,
        },
        created_at=record.created_at,
    )


# ---------- 3. Get All Strings with Filtering ----------
@router.get("/strings")
def get_all_strings(
    is_palindrome: bool | None = Query(None),
    min_length: int | None = Query(None),
    max_length: int | None = Query(None),
    word_count: int | None = Query(None),
    contains_character: str | None = Query(None),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(StringRecord)

        if is_palindrome is not None:
            query = query.filter(StringRecord.is_palindrome == is_palindrome)
        if min_length is not None:
            query = query.filter(StringRecord.length >= min_length)
        if max_length is not None:
            query = query.filter(StringRecord.length <= max_length)
        if word_count is not None:
            query = query.filter(StringRecord.word_count == word_count)
        if contains_character is not None:
            if len(contains_character) != 1:
                raise HTTPException(status_code=400, detail="contains_character must be a single character")
            query = query.filter(StringRecord.value.like(f"%{contains_character}%"))

        records = query.all()
        data = [
            {
                "id": r.sha256_hash,
                "value": r.value,
                "properties": {
                    "length": r.length,
                    "is_palindrome": r.is_palindrome,
                    "unique_characters": r.unique_characters,
                    "word_count": r.word_count,
                    "sha256_hash": r.sha256_hash,
                    "character_frequency_map": r.character_frequency_map,
                },
                "created_at": r.created_at,
            }
            for r in records
        ]

        return {
            "data": data,
            "count": len(data),
            "filters_applied": {
                "is_palindrome": is_palindrome,
                "min_length": min_length,
                "max_length": max_length,
                "word_count": word_count,
                "contains_character": contains_character,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- 4. Natural Language Filtering ----------
@router.get("/strings/filter-by-natural-language")
def filter_by_natural_language(query: str = Query(...), db: Session = Depends(get_db)):
    parsed_filters = {}

    q_lower = query.lower().strip()
    if not q_lower:
        raise HTTPException(status_code=400, detail="Empty query")

    # Simple heuristics
    if "palindromic" in q_lower:
        parsed_filters["is_palindrome"] = True
    if "single word" in q_lower or "one word" in q_lower:
        parsed_filters["word_count"] = 1
    if "longer than" in q_lower:
        try:
            num = int(''.join([c for c in q_lower.split("longer than")[1] if c.isdigit()]))
            parsed_filters["min_length"] = num + 1
        except:
            pass
    if "containing the letter" in q_lower:
        try:
            char = q_lower.split("containing the letter")[1].strip()[0]
            parsed_filters["contains_character"] = char
        except:
            pass
    elif "containing the" in q_lower:
        try:
            char = q_lower.split("containing the")[1].strip()[0]
            parsed_filters["contains_character"] = char
        except:
            pass
    elif "containing the first vowel" in q_lower:
        parsed_filters["contains_character"] = "a"

    if not parsed_filters:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")

    # Reuse existing filter logic
    query_ = db.query(StringRecord)
    if "is_palindrome" in parsed_filters:
        query_ = query_.filter(StringRecord.is_palindrome == parsed_filters["is_palindrome"])
    if "min_length" in parsed_filters:
        query_ = query_.filter(StringRecord.length >= parsed_filters["min_length"])
    if "word_count" in parsed_filters:
        query_ = query_.filter(StringRecord.word_count == parsed_filters["word_count"])
    if "contains_character" in parsed_filters:
        char = parsed_filters["contains_character"]
        query_ = query_.filter(StringRecord.value.like(f"%{char}%"))

    records = query_.all()
    data = [
        {
            "id": r.sha256_hash,
            "value": r.value,
            "properties": {
                "length": r.length,
                "is_palindrome": r.is_palindrome,
                "unique_characters": r.unique_characters,
                "word_count": r.word_count,
                "sha256_hash": r.sha256_hash,
                "character_frequency_map": r.character_frequency_map,
            },
            "created_at": r.created_at,
        }
        for r in records
    ]

    return {
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters,
        },
    }


# ---------- 5. Delete String ----------
@router.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str, db: Session = Depends(get_db)):
    record = db.query(StringRecord).filter(StringRecord.value == string_value).first()
    if not record:
        raise HTTPException(status_code=404, detail="String does not exist")
    db.delete(record)
    db.commit()
    return None
