## Environment setup (M1 Mac)

1. `git clone --recurse-submodules https://github.com/tdsmith/reverse-coattails` (or `git submodule update --init` after cloning)
1. `brew install gdal proj@7`
1. `PROJ_DIR=(brew --prefix proj@7) pip install -r requirements.txt`
1. `dvc pull`

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

1.01-1.03: the Census TIGER/Line shapefiles provide definitions of the VTDs and their names, and relate them to counties and census blocks

1.04   Municipality name
1.05   Municipality type (town, village, etc.)
1.06   Ward (sub-municipal level for cities)

- 1.04-1.06: TIGER/Line also has shapefiles for county subdivisions; we can infer municipality and ward details by observing whether the VTDs intersect a shapefile. There is apparently not a formal promise that a VTD is fully contained by any political subdivision of a state other than a county, though you'd think that would facilitate election administration, so I'm guessing this is a trivial assignment in most cases.
TIGER/Line does *not* generally have shapefiles for all urban wards, at least in Pennsylvania, though some VTDs are named in terms of wards.


1.07   new 2022 state house district number
1.08   new 2022 state senate district number
1.09   new 2022 US House district number

- 1.07-1.09: Redistricting Hub seems to aggregate and republish shapefiles for new legislative districts for Congress and state legislatures, so I think we can intersect the VTDs from TIGER/Line with the new shapefiles to determine how the new VTDs are assigned to districts. Note that 2010 VTDs may have partial overlap with the new districts.

1.10   previous (2020)state house district number
1.11   previous (2020)state senate district number
1.12   previous (2020) US House district number

- 1.10-1.12: TIGER/Line contains legislative districts current to 2018.

2.   Precinct election results
from DRA precinct data (~2016-2020)
2.1   President
2.2   Governor
2.3   US Senator
2.4   Attorney General

2.1-2.4: VEST has this data aligned to 2010 VTDs. The ALARM project has done this for statewide races using a disaggregation/reaggregation method: https://alarm-redist.github.io/posts/2021-08-10-census-2020/ -- so we can take that data directly

from MEDSL *

2.5   US House

2.6   State Senate

2.7   State House

 2.5-2.7: I see that MEDSL has great data on substate races. If we need these aligned to the 2020 VTDs I think we can apply a "crosswalking" method similar to what the ALARM project did with VEST data to project those results onto 2020 VTDs, and it might be possible that someone's already done this. This would probably be the most difficult part of the project.

3.   Precinct-level demographic data:

total population by census groups (e.g. Asian) and group percentages

3.1   2020 Total population

3.2   2020 Voting Age Population (VAP)

3.3   Latest Citizen VAP (probably 2019)
3.4   2010 Total Population

3.5   2010 VAP

3.6   2010 Citizen VAP