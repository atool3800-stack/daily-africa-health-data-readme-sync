#!/usr/bin/env python3
"""
daily_health_summary.py
=======================
Daily analysis + README sync for the South Africa & Egypt health data warehouse.

Scans every JSON Lines file under data/, computes key daily metrics and writes:

  * README.md                          - human/reader-friendly summary (tables & badges)
  * reports/daily_summary_YYYY-MM-DD.json - machine readable report
  * reports/last_sync.json             - state used to compute "new records" across runs

Metrics produced:
  - total records (global + per region)
  - new records since the previous sync (first run: records on the latest date)
  - missing-value ratio per key field (data quality)
  - distribution by disease type / research topic
  - distribution by source type (clinical trial / surveillance / survey)
  - latest data update time + date range
  - repository default branch + latest commit (via GitHub REST API, best-effort)
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request
import urllib.error
from collections import Counter, defaultdict

# --------------------------------------------------------------------------- #
# Paths / config
# --------------------------------------------------------------------------- #
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_ROOT = os.path.join(ROOT, "data")
REPORTS_DIR = os.path.join(ROOT, "reports")
README_PATH = os.path.join(ROOT, "README.md")
LAST_SYNC_PATH = os.path.join(REPORTS_DIR, "last_sync.json")

KEY_FIELDS = [
    "record_id", "region", "country", "province", "city", "date",
    "source_type", "disease_type", "age_group", "sex", "age",
    "cases", "tested", "positive", "population_at_risk",
]

REGION_LABELS = {"South Africa": "South Africa", "Egypt": "Egypt"}

# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def iter_records():
    """Yield all records from data/**/*.jsonl (tolerant to malformed lines)."""
    for dirpath, _dirs, files in os.walk(DATA_ROOT):
        for fname in sorted(files):
            if not fname.endswith(".jsonl"):
                continue
            fpath = os.path.join(dirpath, fname)
            with open(fpath, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(rec, dict):
                        continue
                    rec["_file"] = os.path.relpath(fpath, ROOT)
                    rec["_line"] = lineno
                    yield rec


def _is_missing(value) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def compute_metrics(records):
    """Aggregate raw records into the metric dict used to render the README."""
    total = len(records)
    by_region = Counter(r.get("region") for r in records)
    by_date = Counter(r.get("date") for r in records)
    by_disease = Counter(r.get("disease_type") or "Unknown" for r in records)
    by_topic = Counter(r.get("topic") or "Unknown" for r in records)
    by_source = Counter(r.get("source_type") or "Unknown" for r in records)

    # dates ---------------------------------------------------------------- #
    dates = [d for d in by_date if d]
    max_date = max(dates) if dates else None
    min_date = min(dates) if dates else None
    today = dt.date.today().isoformat()

    # new records since last sync ------------------------------------------ #
    new_records = 0
    new_by_region = Counter()
    last_sync = {}
    if os.path.exists(LAST_SYNC_PATH):
        try:
            with open(LAST_SYNC_PATH, encoding="utf-8") as fh:
                last_sync = json.load(fh)
        except (json.JSONDecodeError, OSError):
            last_sync = {}
    prev_max_date = last_sync.get("max_date")

    if prev_max_date and prev_max_date >= max_date:
        # no new data since last sync
        new_records = 0
        new_by_region = Counter()
    else:
        cutoff = prev_max_date or max_date
        for r in records:
            if r.get("date") and r["date"] >= cutoff:
                new_records += 1
                new_by_region[r.get("region")] += 1

    # missing values -------------------------------------------------------- #
    missing = {}
    for field in KEY_FIELDS:
        missing[field] = sum(1 for r in records if _is_missing(r.get(field)))
    missing_ratio = {
        f: (missing[f] / total * 100 if total else 0.0) for f in KEY_FIELDS
    }
    # overall data-quality completeness (avg over key fields)
    avg_missing = sum(missing_ratio.values()) / len(missing_ratio)
    completeness = 100.0 - avg_missing

    # region / date breakdowns for tables ----------------------------------- #
    region_rows = []
    for region in ["South Africa", "Egypt"]:
        cnt = by_region.get(region, 0)
        region_rows.append({
            "region": region,
            "count": cnt,
            "pct": (cnt / total * 100) if total else 0.0,
            "new": new_by_region.get(region, 0),
        })

    disease_rows = []
    for disease, cnt in by_disease.most_common():
        disease_rows.append({
            "disease": disease,
            "count": cnt,
            "pct": (cnt / total * 100) if total else 0.0,
        })

    source_rows = []
    for src, cnt in by_source.most_common():
        source_rows.append({
            "source": src,
            "count": cnt,
            "pct": (cnt / total * 100) if total else 0.0,
        })

    return {
        "total": total,
        "today": today,
        "max_date": max_date,
        "min_date": min_date,
        "files": len(set(r["_file"] for r in records)),
        "by_region": dict(by_region),
        "by_disease": dict(by_disease),
        "by_topic": dict(by_topic),
        "by_source": dict(by_source),
        "by_date": dict(sorted(by_date.items())),
        "new_records": new_records,
        "new_by_region": dict(new_by_region),
        "missing": missing,
        "missing_ratio": missing_ratio,
        "completeness": completeness,
        "region_rows": region_rows,
        "disease_rows": disease_rows,
        "source_rows": source_rows,
    }


# --------------------------------------------------------------------------- #
# GitHub REST API (best-effort) -- default branch + latest commit
# --------------------------------------------------------------------------- #
def github_repo_info():
    """Fetch {default_branch, latest_commit} for the repository."""
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "atool3800-stack/daily-africa-health-data-readme-sync")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "health-data-sync-bot",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    info = {"default_branch": None, "latest_commit": None}

    def _get(url):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.HTTPError, OSError, json.JSONDecodeError):
            return None

    repo = _get(f"https://api.github.com/repos/{repo_slug}")
    if repo and repo.get("default_branch"):
        info["default_branch"] = repo["default_branch"]
        commits = _get(f"https://api.github.com/repos/{repo_slug}/commits?per_page=1")
        if commits and isinstance(commits, list) and commits:
            c = commits[0]
            commit = c.get("commit", {})
            info["latest_commit"] = {
                "sha": c.get("sha", "")[:7],
                "message": (commit.get("message") or "").splitlines()[0],
                "date": commit.get("committer", {}).get("date"),
                "author": (commit.get("author") or {}).get("name"),
            }
    return info


# --------------------------------------------------------------------------- #
# README rendering
# --------------------------------------------------------------------------- #
def fmt_pct(x):
    return f"{x:.1f}%"


def render_badges(m):
    from urllib.parse import quote

    def enc(s):
        # shields.io uses '-' as the segment separator -> encode it too
        return quote(s, safe="")

    badges = [
        ("records", f"{m['total']:,}", "blue"),
        ("last update", str(m["max_date"]), "brightgreen"),
        ("regions", "2", "orange"),
        ("data completeness", fmt_pct(m["completeness"]), "green"),
        ("new records", str(m["new_records"]), "yellow"),
    ]
    lines = []
    for label, value, color in badges:
        lines.append(
            f"![{label}](https://img.shields.io/badge/{enc(label)}-{enc(value)}-{color})"
        )
    return " ".join(lines)


def render_readme(m, repo):
    today = m["today"]
    default_branch = repo["default_branch"] or "main"
    commit = repo["latest_commit"] or {}
    commit_line = "—"
    if commit:
        commit_line = (f"[`{commit['sha']}`](https://github.com/"
                       f"atool3800-stack/daily-africa-health-data-readme-sync/"
                       f"commit/{commit['sha']}) `{commit['message']}` "
                       f"({commit['date'] or ''})")

    lines = []
    A = lines.append

    A("# 🏥 Africa Health Data Warehouse — Daily Summary")
    A("")
    A("Structured public-health records for **South Africa** and **Egypt** collected "
      "from **clinical trials**, **public-health surveillance** and "
      "**epidemiological surveys**. This page is regenerated automatically every day "
      "by a scheduled GitHub Actions workflow and is intended for **academic "
      "researchers**.")
    A("")
    A(render_badges(m))
    A("")
    A("---")
    A("")
    A("## 📊 每日数据摘要 / Daily Data Summary")
    A("")
    A(f"*Generated at **{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}** "
      f"from {m['files']} data file(s).*")
    A("")
    A("| Metric | Value |")
    A("| --- | --- |")
    A(f"| **Total records** | {m['total']:,} |")
    A(f"| **New records (since last sync)** | {m['new_records']:,} |")
    A(f"| **Regions covered** | 2 (South Africa, Egypt) |")
    A(f"| **Date range** | {m['min_date']} → {m['max_date']} |")
    A(f"| **Latest data update** | {m['max_date']} |")
    A(f"| **Data completeness** | {fmt_pct(m['completeness'])} |")
    A(f"| **Default branch** | `{default_branch}` |")
    A(f"| **Latest commit** | {commit_line} |")
    A("")
    A("---")
    A("")
    A("## 🌍 地区分布 / Regional Distribution")
    A("")
    A("| Region | Records | Share | New (latest batch) |")
    A("| --- | ---: | ---: | ---: |")
    for row in m["region_rows"]:
        A(f"| {row['region']} | {row['count']:,} | {fmt_pct(row['pct'])} | {row['new']:,} |")
    A(f"| **Total** | **{m['total']:,}** | 100.0% | **{m['new_records']:,}** |")
    A("")
    A("### By source type")
    A("")
    A("| Source | Records | Share |")
    A("| --- | ---: | ---: |")
    for row in m["source_rows"]:
        A(f"| {row['source']} | {row['count']:,} | {fmt_pct(row['pct'])} |")
    A("")
    A("### By disease type / research topic")
    A("")
    A("| Disease / Topic | Records | Share |")
    A("| --- | ---: | ---: |")
    for row in m["disease_rows"]:
        A(f"| {row['disease']} | {row['count']:,} | {fmt_pct(row['pct'])} |")
    A("")
    A("---")
    A("")
    A("## 🔍 数据质量报告 / Data Quality Report")
    A("")
    A("Missing-value ratio is computed on the key fields below. A value is treated "
      "as missing when it is `null` or an empty string.")
    A("")
    A("| Field | Missing | Missing ratio |")
    A("| --- | ---: | ---: |")
    for field in KEY_FIELDS:
        A(f"| `{field}` | {m['missing'][field]:,} | {fmt_pct(m['missing_ratio'][field])} |")
    A("")
    A(f"**Overall completeness:** {fmt_pct(m['completeness'])}")
    A("")
    A("---")
    A("")
    A("## 📈 近30天记录趋势 / 30-Day Trend")
    A("")
    A("| Date | Records |")
    A("| --- | ---: |")
    recent = sorted(m["by_date"].items())[-30:]
    for d, cnt in recent:
        A(f"| {d} | {cnt:,} |")
    A("")
    A("---")
    A("")
    A("## 📚 数据来源说明 / Data Sources")
    A("")
    A("Records in `data/` are aggregated from three public-health research streams:")
    A("")
    A("| Stream | Description |")
    A("| --- | --- |")
    A("| **Clinical trials** (`clinical_trial`) | Interventional/observational trial "
      "records with a study identifier |")
    A("| **Public-health surveillance** (`public_health_surveillance`) | Routine "
      "notifiable-disease & syndromic surveillance reporting |")
    A("| **Epidemiological surveys** (`epidemiological_survey`) | Cross-sectional & "
      "cohort field surveys |")
    A("")
    A("> ⚠️ **Note:** all records are **synthetic / anonymised** for demonstration and "
      "research-engineering purposes. They must not be used for clinical decision "
      "making. Replace with your institution's approved, de-identified source data "
      "before publication.")
    A("")
    A("## 🗂️ 字段字典 / Field Dictionary")
    A("")
    A("A complete description of every field (type, allowed values, units) is "
      "available in [`docs/FIELD_DICTIONARY.md`](docs/FIELD_DICTIONARY.md).")
    A("")
    A("| Field | Description |")
    A("| --- | --- |")
    A("| `record_id` | Unique record identifier (region + date + sequence) |")
    A("| `region` / `country` | Geographic scope (`South Africa` / `Egypt`) |")
    A("| `province` / `city` | Sub-national location (may be missing) |")
    A("| `date` | Observation date (ISO `YYYY-MM-DD`) |")
    A("| `source_type` | Data stream (see Data Sources) |")
    A("| `disease_type` | Disease or health-condition category |")
    A("| `topic` | Research topic label |")
    A("| `age_group` / `age` | Age band / age in years (may be missing) |")
    A("| `sex` | Biological sex `F` / `M` (may be missing) |")
    A("| `cases` | Number of cases in the observation unit |")
    A("| `tested` / `positive` | Testing volume and positives |")
    A("| `population_at_risk` | Denominator population estimate |")
    A("| `study_id` | Clinical-trial identifier (null for other streams) |")
    A("")
    A("## 📄 引用与使用说明 / Citation & Usage")
    A("")
    A("If you use this repository in academic work, please cite it as:")
    A("")
    A("```bibtex")
    A("@misc{africa_health_warehouse_2026,")
    A("  title        = {Africa Health Data Warehouse: South Africa \\& Egypt Daily Summary},")
    A("  author       = {Health Data Engineering Team},")
    A("  year         = {2026},")
    A("  howpublished = {GitHub Repository},")
    A("  note         = {Latest data update: " + str(m["max_date"]) + ", retrieved " + today + "},")
    A("  url          = {https://github.com/atool3800-stack/daily-africa-health-data-readme-sync}")
    A("}")
    A("```")
    A("")
    A("**Usage notes for researchers:**")
    A("")
    A("- Data is stored as **JSON Lines** under `data/<region>/<date>.jsonl` — one "
      "JSON object per line, easy to stream with `jsonlines`, `pandas`, `duckdb` or `jq`.")
    A("- Run `python scripts/daily_health_summary.py` to recompute this summary "
      "locally; the GitHub Actions workflow does the same on schedule.")
    A("- See [`docs/FIELD_DICTIONARY.md`](docs/FIELD_DICTIONARY.md) for the field "
      "dictionary and [`scripts/`](scripts/) for reproducible analysis code.")
    A("- License / provenance details and contribution guidelines: see "
      "[`LICENSE`](LICENSE) and [`CONTRIBUTING.md`](CONTRIBUTING.md).")
    A("")
    A("---")
    A("")
    A("_Maintained by the Health Data Engineering Team · Automated daily sync via "
      "GitHub Actions (UTC+2 / South Africa · Egypt)._")

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    records = list(iter_records())
    metrics = compute_metrics(records)
    repo = github_repo_info()

    readme = render_readme(metrics, repo)
    with open(README_PATH, "w", encoding="utf-8") as fh:
        fh.write(readme + "\n")

    # machine readable daily report
    report = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "max_date": metrics["max_date"],
        "total_records": metrics["total"],
        "new_records": metrics["new_records"],
        "records_by_region": metrics["by_region"],
        "records_by_disease": metrics["by_disease"],
        "records_by_source": metrics["by_source"],
        "missing_ratio": {k: round(v, 2) for k, v in metrics["missing_ratio"].items()},
        "completeness": round(metrics["completeness"], 2),
        "default_branch": repo["default_branch"],
        "latest_commit": repo["latest_commit"],
    }
    report_path = os.path.join(REPORTS_DIR, f"daily_summary_{metrics['max_date']}.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    # sync state for the next run
    with open(LAST_SYNC_PATH, "w", encoding="utf-8") as fh:
        json.dump({
            "last_sync_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "max_date": metrics["max_date"],
            "total_records": metrics["total"],
        }, fh, indent=2)

    print(f"README.md updated: {metrics['total']} records, "
          f"new={metrics['new_records']}, completeness={metrics['completeness']:.1f}%")
    print(f"Report written: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
