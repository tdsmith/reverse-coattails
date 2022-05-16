## Environment setup (M1 Mac)

1. `brew install gdal`
1. `PROJ_DIR=(brew --prefix proj@7) pip install -r requirements.txt`

## Data sources

1.  Precinct (VTD) and district identification

VTDs are statistical units and not adminstrative units so VTDs are not 1:1 associated with precincts;
a single VTD can contain many precincts, or many VTDs could exist within a precinct.
Aligning electoral maps to Census VTDs is optional, though most states do, so there is hopefully an integral
relationship between VTDs and precincts.

VTDs are not fixed between census cycles.

A voting district is guaranteed to be smaller than a county but may have an unknown relationship with smaller political entities.

1.01   Precinct name
1.02   Precinct Geocode ID
1.03   County name


1.04   Municipality name
1.05   Municipality type (town, village, etc.)
1.06   Ward (sub-municipal level for cities)

Redistricting Data Hub appears to be a fairly comprehensive source of post-2020 district shapefiles.

1.07   new 2022 state house district number
1.08   new 2022 state senate district number
1.09   new 2022 US House district number


1.10   previous (2020)state house district number
1.11   previous (2020)state senate district number
1.12   previous (2020) US House district number

2.   Precinct election results
from DRA precinct data (~2016-2020)
2.1   President
2.2   Governor
2.3   US Senator
2.4   Attorney General

from MEDSL *

2.5   US House

2.6   State Senate

2.7   State House

 

3.   Precinct-level demographic data:

total population by census groups (e.g. Asian) and group percentages

3.1   2020 Total population

3.2   2020 Voting Age Population (VAP)

3.3   Latest Citizen VAP (probably 2019)
3.4   2010 Total Population

3.5   2010 VAP

3.6   2010 Citizen VAP