# Contributing

Thanks for helping improve the Africa Health Data Warehouse!

## Data

- Append new observations as **JSON Lines** under `data/<region>/<YYYY-MM-DD>.jsonl`.
- Do not modify historical files — keep the record history append-only.
- Preserve the schema documented in [`docs/FIELD_DICTIONARY.md`](docs/FIELD_DICTIONARY.md).
- Anonymise / de-identify all personal data before adding it to the repository.

## Code

1. Fork the repository and create a feature branch.
2. Run the analysis locally to verify it still works:
   ```bash
   python scripts/daily_health_summary.py
   ```
3. Open a Pull Request describing the change and any effect on the generated
   `README.md` / reports.

## Issues

Please file an issue for:
- suspected data-quality problems (missing values, outliers),
- new disease categories or regions to cover,
- improvements to the daily automation workflow.
