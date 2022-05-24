import csv
import io
import zipfile
from pathlib import Path
from typing import List

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

def read_crosswalks(state_fips: List[str] = []) -> pd.DataFrame:
    """Read crosswalks into a tabular format.

    Crosswalks are specified in a format like:
        GEOID20,GEOID10,x
    where x is the fraction of the GEOID10 block that GEOID20 occupies.
    (The official datasets use area; the VEST crosswalks by Brian Amos which we
    use here use a land-use database to try and weight by residential density.)

    Of course, a GEOID20 may overlap more than one GEOID10! In the dataset,
    this looks like
        GEOID20,GEOID10_a,x,GEOID10_b,y

    This function produces a table with one row per relationship instead, like:
        GEOID20,GEOID10_a,x
        GEOID20,GEOID10_b,y
    """
    zf_path = (root / "data-raw/amos_crosswalks/block10block20_crosswalks.zip")
    zf = zipfile.ZipFile(zf_path)

    csvs = [name for name in zf.namelist() if name.endswith(".csv")]
    int_fips = [int(i) for i in state_fips]
    records = []

    for csv_filename in csvs:
        state = csv_filename.rsplit(".", maxsplit=1)[0].rsplit("_", maxsplit=1)[1]
        if int_fips:
            if int(state) not in int_fips:
                continue
        f = zf.open(csv_filename, "r")
        wrapper = io.TextIOWrapper(f, "ascii", newline="")
        reader = csv.reader(wrapper)
        for line in reader:
            geoid20 = line[0]
            for i in range(1, len(line), 2):
                geoid10, weight = line[i], line[i+1]
                records.append((state, geoid20, geoid10, weight))
        f.close()
    return pd.DataFrame(records, columns=["STATE", "GEOID20", "GEOID10", "weight"])
