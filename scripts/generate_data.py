#!/usr/bin/env python3
"""
generate_data.py
================
One-time / periodic generator of synthetic (but realistic) public-health records
for the South Africa & Egypt health data warehouse.

Record domains:
  - clinical_trial              (临床试验)
  - public_health_surveillance  (公共卫生监测)
  - epidemiological_survey      (流行病学调查)

Each daily batch is written to data/<region_slug>/<YYYY-MM-DD>.jsonl so the
daily README sync workflow can detect "new records" by date.

Fields intentionally contain some missing values so the Data Quality Report in
README.md is meaningful.
"""

import json
import os
import random
import datetime

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
DATA_ROOT = os.path.join(os.path.dirname(__file__), "..", "data")
DAYS_BACK = 35                      # generate the last N days of batches
BASE_DATE = datetime.date(2026, 8, 13)  # "today" in the simulation
RECORDS_PER_DAY_RANGE = (80, 160)   # daily batch size range (per region)

SEED = 20260813

# Region -> provinces/cities and disease burden profile
REGIONS = {
    "South Africa": {
        "slug": "south_africa",
        "provinces": {
            "Gauteng": ["Johannesburg", "Pretoria", "Soweto"],
            "Western Cape": ["Cape Town", "Stellenbosch", "George"],
            "KwaZulu-Natal": ["Durban", "Pietermaritzburg", "Newcastle"],
            "Eastern Cape": ["Gqeberha", "East London", "Mthatha"],
            "Limpopo": ["Polokwane", "Tzaneen", "Thohoyandou"],
        },
        "diseases": [
            "HIV/AIDS", "Tuberculosis", "COVID-19", "Diabetes Mellitus",
            "Hypertension", "Malaria", "Cholera", "Maternal Health",
            "Childhood Immunization", "Mental Health",
        ],
    },
    "Egypt": {
        "slug": "egypt",
        "provinces": {
            "Cairo": ["Cairo", "Helwan", "Nasr City"],
            "Giza": ["Giza", "6th of October", "Imbaba"],
            "Alexandria": ["Alexandria", "Borg El Arab", "Amreya"],
            "Qalyubia": ["Banha", "Shubra El Kheima", "Qalyub"],
            "Aswan": ["Aswan", "Edfu", "Kom Ombo"],
        },
        "diseases": [
            "Hepatitis C", "Schistosomiasis", "Diabetes Mellitus",
            "Hypertension", "COVID-19", "Cholera", "Dengue Fever",
            "Maternal Health", "Tuberculosis", "Kidney Disease",
        ],
    },
}

SOURCE_TYPES = ["clinical_trial", "public_health_surveillance", "epidemiological_survey"]
SOURCE_WEIGHTS = [0.30, 0.45, 0.25]

AGE_GROUPS = ["0-4", "5-17", "18-39", "40-59", "60+"]
SEXES = ["F", "M"]


def make_record(region: str, rng: random.Random, day: datetime.date, idx: int) -> dict:
    """Build one JSON record (some fields may be None to simulate missing data)."""
    prov, city = rng.choice(list(REGIONS[region]["provinces"].items()))
    city = rng.choice(city)
    disease = rng.choice(REGIONS[region]["diseases"])
    source = rng.choices(SOURCE_TYPES, weights=SOURCE_WEIGHTS, k=1)[0]

    prefix = "ZA" if region == "South Africa" else "EG"
    record = {
        "record_id": f"{prefix}-{day:%Y%m%d}-{idx:05d}",
        "region": region,
        "country": region,
        "province": prov,
        "city": city,
        "date": day.isoformat(),
        "source_type": source,
        "disease_type": disease,
        "topic": f"{disease} surveillance & control",
        "age_group": rng.choice(AGE_GROUPS),
        "sex": rng.choice(SEXES),
        "age": rng.randint(0, 95),
        "cases": rng.randint(1, 800),
        "tested": rng.randint(10, 5000),
        "positive": rng.randint(0, 900),
        "population_at_risk": rng.randint(500, 500000),
    }

    if source == "clinical_trial":
        record["study_id"] = f"{prefix}-CT-{rng.randint(1000, 9999)}"
    else:
        record["study_id"] = None

    # ---- simulate missing values (data quality) --------------------------- #
    # ~6% missing age, ~5% missing sex, ~9% missing cases, ~12% missing tested
    if rng.random() < 0.06:
        record["age"] = None
        record["age_group"] = None
    if rng.random() < 0.05:
        record["sex"] = None
    if rng.random() < 0.09:
        record["cases"] = None
    if rng.random() < 0.12:
        record["tested"] = None
        record["positive"] = None
    if rng.random() < 0.04:
        record["city"] = None

    return record


def main() -> None:
    rng = random.Random(SEED)
    os.makedirs(DATA_ROOT, exist_ok=True)

    total = 0
    for region, cfg in REGIONS.items():
        region_dir = os.path.join(DATA_ROOT, cfg["slug"])
        os.makedirs(region_dir, exist_ok=True)
        for offset in range(DAYS_BACK, -1, -1):   # oldest -> newest
            day = BASE_DATE - datetime.timedelta(days=offset)
            n = rng.randint(*RECORDS_PER_DAY_RANGE)
            path = os.path.join(region_dir, f"{day.isoformat()}.jsonl")
            with open(path, "w", encoding="utf-8") as fh:
                for i in range(n):
                    rec = make_record(region, rng, day, i + 1)
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += n
    print(f"Generated {total} records across {len(REGIONS)} regions "
          f"({DAYS_BACK + 1} daily batches each).")


if __name__ == "__main__":
    main()
