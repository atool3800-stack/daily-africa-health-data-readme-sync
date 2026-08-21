# 🏥 Africa Health Data Warehouse — Daily Summary

Structured public-health records for **South Africa** and **Egypt** collected from **clinical trials**, **public-health surveillance** and **epidemiological surveys**. This page is regenerated automatically every day by a scheduled GitHub Actions workflow and is intended for **academic researchers**.

![records](https://img.shields.io/badge/records-8%2C509-blue) ![last update](https://img.shields.io/badge/last%20update-2026-08-13-brightgreen) ![regions](https://img.shields.io/badge/regions-2-orange) ![data completeness](https://img.shields.io/badge/data%20completeness-96.4%25-green) ![new records](https://img.shields.io/badge/new%20records-262-yellow)

---

## 📊 每日数据摘要 / Daily Data Summary

*Generated at **2026-08-21 04:25 UTC** from 72 data file(s).*

| Metric | Value |
| --- | --- |
| **Total records** | 8,509 |
| **New records (latest batch)** | 262 |
| **Regions covered** | 2 (South Africa, Egypt) |
| **Date range** | 2026-07-09 → 2026-08-13 |
| **Latest data update** | 2026-08-13 |
| **Data completeness** | 96.4% |
| **Default branch** | `main` |
| **Latest commit** | [`81608e7`](https://github.com/atool3800-stack/daily-africa-health-data-readme-sync/commit/81608e7) `daily(readme): update health data summary 2026-08-20` (2026-08-20T04:23:34Z) |

---

## 🌍 地区分布 / Regional Distribution

| Region | Records | Share | New (latest batch) |
| --- | ---: | ---: | ---: |
| South Africa | 4,248 | 49.9% | 133 |
| Egypt | 4,261 | 50.1% | 129 |
| **Total** | **8,509** | 100.0% | **262** |

### By source type

| Source | Records | Share |
| --- | ---: | ---: |
| public_health_surveillance | 3,837 | 45.1% |
| clinical_trial | 2,589 | 30.4% |
| epidemiological_survey | 2,083 | 24.5% |

### By disease type / research topic

| Disease / Topic | Records | Share |
| --- | ---: | ---: |
| Cholera | 875 | 10.3% |
| Maternal Health | 874 | 10.3% |
| Tuberculosis | 827 | 9.7% |
| Hypertension | 809 | 9.5% |
| Diabetes Mellitus | 805 | 9.5% |
| COVID-19 | 788 | 9.3% |
| Hepatitis C | 485 | 5.7% |
| Childhood Immunization | 469 | 5.5% |
| HIV/AIDS | 456 | 5.4% |
| Schistosomiasis | 452 | 5.3% |
| Dengue Fever | 421 | 4.9% |
| Kidney Disease | 418 | 4.9% |
| Mental Health | 418 | 4.9% |
| Malaria | 412 | 4.8% |

---

## 🔍 数据质量报告 / Data Quality Report

Missing-value ratio is computed on the key fields below. A value is treated as missing when it is `null` or an empty string.

| Field | Missing | Missing ratio |
| --- | ---: | ---: |
| `record_id` | 0 | 0.0% |
| `region` | 0 | 0.0% |
| `country` | 0 | 0.0% |
| `province` | 0 | 0.0% |
| `city` | 320 | 3.8% |
| `date` | 0 | 0.0% |
| `source_type` | 0 | 0.0% |
| `disease_type` | 0 | 0.0% |
| `age_group` | 504 | 5.9% |
| `sex` | 401 | 4.7% |
| `age` | 504 | 5.9% |
| `cases` | 754 | 8.9% |
| `tested` | 1,048 | 12.3% |
| `positive` | 1,048 | 12.3% |
| `population_at_risk` | 0 | 0.0% |

**Overall completeness:** 96.4%

---

## 📈 近30天记录趋势 / 30-Day Trend

| Date | Records |
| --- | ---: |
| 2026-07-15 | 193 |
| 2026-07-16 | 247 |
| 2026-07-17 | 268 |
| 2026-07-18 | 239 |
| 2026-07-19 | 216 |
| 2026-07-20 | 231 |
| 2026-07-21 | 291 |
| 2026-07-22 | 260 |
| 2026-07-23 | 275 |
| 2026-07-24 | 228 |
| 2026-07-25 | 199 |
| 2026-07-26 | 183 |
| 2026-07-27 | 185 |
| 2026-07-28 | 196 |
| 2026-07-29 | 229 |
| 2026-07-30 | 263 |
| 2026-07-31 | 256 |
| 2026-08-01 | 232 |
| 2026-08-02 | 261 |
| 2026-08-03 | 239 |
| 2026-08-04 | 280 |
| 2026-08-05 | 186 |
| 2026-08-06 | 184 |
| 2026-08-07 | 223 |
| 2026-08-08 | 306 |
| 2026-08-09 | 251 |
| 2026-08-10 | 313 |
| 2026-08-11 | 221 |
| 2026-08-12 | 238 |
| 2026-08-13 | 262 |

---

## 📚 数据来源说明 / Data Sources

Records in `data/` are aggregated from three public-health research streams:

| Stream | Description |
| --- | --- |
| **Clinical trials** (`clinical_trial`) | Interventional/observational trial records with a study identifier |
| **Public-health surveillance** (`public_health_surveillance`) | Routine notifiable-disease & syndromic surveillance reporting |
| **Epidemiological surveys** (`epidemiological_survey`) | Cross-sectional & cohort field surveys |

> ⚠️ **Note:** all records are **synthetic / anonymised** for demonstration and research-engineering purposes. They must not be used for clinical decision making. Replace with your institution's approved, de-identified source data before publication.

## 🗂️ 字段字典 / Field Dictionary

A complete description of every field (type, allowed values, units) is available in [`docs/FIELD_DICTIONARY.md`](docs/FIELD_DICTIONARY.md).

| Field | Description |
| --- | --- |
| `record_id` | Unique record identifier (region + date + sequence) |
| `region` / `country` | Geographic scope (`South Africa` / `Egypt`) |
| `province` / `city` | Sub-national location (may be missing) |
| `date` | Observation date (ISO `YYYY-MM-DD`) |
| `source_type` | Data stream (see Data Sources) |
| `disease_type` | Disease or health-condition category |
| `topic` | Research topic label |
| `age_group` / `age` | Age band / age in years (may be missing) |
| `sex` | Biological sex `F` / `M` (may be missing) |
| `cases` | Number of cases in the observation unit |
| `tested` / `positive` | Testing volume and positives |
| `population_at_risk` | Denominator population estimate |
| `study_id` | Clinical-trial identifier (null for other streams) |

## 📄 引用与使用说明 / Citation & Usage

If you use this repository in academic work, please cite it as:

```bibtex
@misc{africa_health_warehouse_2026,
  title        = {Africa Health Data Warehouse: South Africa \& Egypt Daily Summary},
  author       = {Health Data Engineering Team},
  year         = {2026},
  howpublished = {GitHub Repository},
  note         = {Latest data update: 2026-08-13, retrieved 2026-08-21},
  url          = {https://github.com/atool3800-stack/daily-africa-health-data-readme-sync}
}
```

**Usage notes for researchers:**

- Data is stored as **JSON Lines** under `data/<region>/<date>.jsonl` — one JSON object per line, easy to stream with `jsonlines`, `pandas`, `duckdb` or `jq`.
- Run `python scripts/daily_health_summary.py` to recompute this summary locally; the GitHub Actions workflow does the same on schedule.
- See [`docs/FIELD_DICTIONARY.md`](docs/FIELD_DICTIONARY.md) for the field dictionary and [`scripts/`](scripts/) for reproducible analysis code.
- License / provenance details and contribution guidelines: see [`LICENSE`](LICENSE) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

_Maintained by the Health Data Engineering Team · Automated daily sync via GitHub Actions (UTC+2 / South Africa · Egypt)._
