# Field Dictionary — Africa Health Data Warehouse

Each line in a `data/<region>/<date>.jsonl` file is a JSON object (record).
Below is the full description of every field: type, allowed values and units.

| Field | Type | Required | Allowed values / Units | Description |
| --- | --- | --- | --- | --- |
| `record_id` | string | yes | `ZA-YYYYMMDD-NNNNN` / `EG-YYYYMMDD-NNNNN` | Unique record identifier (region prefix + observation date + 5-digit sequence). |
| `region` | string | yes | `South Africa`, `Egypt` | Geographic region. |
| `country` | string | yes | `South Africa`, `Egypt` | ISO country name (currently identical to `region`). |
| `province` | string | yes | see below | Sub-national province / governorate. |
| `city` | string | no | free text | City / district. May be missing (≈4%). |
| `date` | string | yes | `YYYY-MM-DD` | Observation date (ISO 8601). |
| `source_type` | string | yes | `clinical_trial`, `public_health_surveillance`, `epidemiological_survey` | Data stream the record belongs to. |
| `disease_type` | string | yes | e.g. `HIV/AIDS`, `Tuberculosis`, `Hepatitis C`, `Malaria`, ... | Disease or health-condition category. |
| `topic` | string | yes | free text | Research topic label (usually `"<disease> surveillance & control"`). |
| `age_group` | string | no | `0-4`, `5-17`, `18-39`, `40-59`, `60+` | Age band. May be missing (≈6%). |
| `age` | integer | no | 0–95 years | Age in years. May be missing (≈6%). |
| `sex` | string | no | `F`, `M` | Biological sex. May be missing (≈5%). |
| `cases` | integer | no | ≥ 0 | Number of cases in the observation unit. May be missing (≈9%). |
| `tested` | integer | no | ≥ 0 | Number of tests performed. May be missing (≈12%). |
| `positive` | integer | no | ≥ 0 | Number of positive test results. May be missing (≈12%). |
| `population_at_risk` | integer | no | ≥ 0 | Denominator population estimate at risk. |
| `study_id` | string | no | `ZA-CT-####` / `EG-CT-####` | Clinical-trial study identifier. Only present when `source_type == clinical_trial`, otherwise `null`. |

## Province / governorate values

**South Africa** (province → cities):
- Gauteng → Johannesburg, Pretoria, Soweto
- Western Cape → Cape Town, Stellenbosch, George
- KwaZulu-Natal → Durban, Pietermaritzburg, Newcastle
- Eastern Cape → Gqeberha, East London, Mthatha
- Limpopo → Polokwane, Tzaneen, Thohoyandou

**Egypt** (governorate → cities):
- Cairo → Cairo, Helwan, Nasr City
- Giza → Giza, 6th of October, Imbaba
- Alexandria → Alexandria, Borg El Arab, Amreya
- Qalyubia → Banha, Shubra El Kheima, Qalyub
- Aswan → Aswan, Edfu, Kom Ombo

## Missing values

Missing values are encoded as JSON `null` (or an empty string, which the summary
script also treats as missing). The Data Quality Report in `README.md` lists the
missing-value ratio for every key field.

## Reading the data

```bash
# stream with jq
jq -c 'select(.region=="South Africa")' data/south_africa/*.jsonl

# stream with pandas
import pandas as pd
df = pd.concat(
    [pd.read_json(p, lines=True) for p in snakemake.glob_wildcards("data/{r}/{d}.jsonl")],
    ignore_index=True,
)
```
