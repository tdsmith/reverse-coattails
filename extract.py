from pathlib import Path

import pandas as pd

root = Path(__file__).parent

medsl_dtypes = {
    "precinct": str,
    "office": str,
    "party_detailed": str,
    "party_simplified": str,
    "mode": str,
    "votes": int,
    "county_name": str,
    "county_fips": str,
    "jurisdiction_name": str,
    "jurisdiction_fips": str,
    "candidate": str,
    "district": str,
    "dataverse": str,
    "year": int,
    "stage": "category",
    "state": str,
    "special": bool,
    "writein": bool,
    "state_po": str,
    "state_fips": str,
    "state_cen": str,
    "state_ic": str,
    "date": str,
    "readme_check": bool,
    "magnitude": int,
}

## medsl

medsl_path = root/"data-raw/medsl/2020-elections-official"

def medsl_local() -> pd.DataFrame:
    path = medsl_path / "LOCAL/LOCAL_precinct_general.zip"
    return pd.read_csv(path, dtype=medsl_dtypes)

def medsl_state() -> pd.DataFrame:
    path = medsl_path / "STATE/STATE_precinct_general.zip"
    return pd.read_csv(path, dtype=medsl_dtypes)

def medsl_house() -> pd.DataFrame:
    path = medsl_path / "HOUSE/HOUSE_precinct_general.zip"
    return pd.read_csv(path, dtype=medsl_dtypes)