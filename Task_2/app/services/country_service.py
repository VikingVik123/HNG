import requests, random
from datetime import datetime
from sqlmodel import Session, select
from app.models.country import Country

COUNTRIES_API = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
EXCHANGE_API = "https://open.er-api.com/v6/latest/USD"

def fetch_country_data():
    try:
        countries = requests.get(COUNTRIES_API, timeout=15).json()
        rates = requests.get(EXCHANGE_API, timeout=15).json().get("rates", {})
    except Exception:
        raise Exception("External data source unavailable")

    data = []
    for c in countries:
        name = c.get("name")
        population = c.get("population", 0)
        currency_code = None
        exchange_rate = None
        estimated_gdp = None

        if c.get("currencies"):
            currency_code = c["currencies"][0].get("code")

        if currency_code and currency_code in rates:
            exchange_rate = rates[currency_code]
            rand_val = random.randint(1000, 2000)
            estimated_gdp = (population * rand_val) / exchange_rate
        else:
            estimated_gdp = 0

        data.append({
            "name": name,
            "capital": c.get("capital"),
            "region": c.get("region"),
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": c.get("flag"),
            "last_refreshed_at": datetime.utcnow()
        })
    return data

def refresh_countries(session: Session):
    countries_data = fetch_country_data()
    for item in countries_data:
        existing = session.exec(select(Country).where(Country.name == item["name"])).first()
        if existing:
            for key, value in item.items():
                setattr(existing, key, value)
        else:
            session.add(Country(**item))
    session.commit()
    return len(countries_data)
