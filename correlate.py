import warnings

import attr
import geopandas as gpd
import pandas as pd


@attr.define
class OverlayResult:
    """The result of overlay(), including diagnosics.

    `within` and `contained` are a Series of indices from `augment`,
    indexed by the index of `df`.

    within: the elements of `df` that were completely within an element of `augment`
    contained: the elements of `df` that completely contained an element of `augment`

    intersected: Represents incomplete overlaps between the geographies of `df` and `augment`.
        The outer dictionary is keyed by an index of `df`.
        Each inner Series is indexed by an index of `augment` and represents the fraction
        of the area of `df` that is inside the corresponding element of `augment`.
    
    no_match: the elements of `df` that had nothing to do with any element of `augment`

    overlaid: the data frame resulting from joining the unique columns of augmented onto df
        using a spatial join
    """
    within: pd.Series
    contained: pd.Series
    intersected: dict[str, pd.Series]
    no_match: pd.Index

    overlaid: gpd.GeoDataFrame

    def format_summary(self) -> str:
        return "\n".join(
            [
                f"Within: {len(self.within)}",
                f"Contained: {len(self.contained)}",
                f"Partial: {len(self.intersected)}",
                f"No match: {len(self.no_match)}",
            ]
        )


def overlay(df: gpd.GeoDataFrame, augment: gpd.GeoDataFrame) -> OverlayResult:
    """Spatially left-joins columns of `augment` onto `df`.

    In this package, the rows of `df` each represent a census VTD.
    `augment` contains the shapes of political entities and some facts about them.
    The goal of this function is, for each element of `df`, to find the most-matching row of `augment`
    and join those facts onto `df`.

    One row of `df` is only ever joined to a single row of `augment` and no mixing or averaging is performed.
    A row of `augment` may be joined to many rows of `df`.
    """
    keep_columns = [c for c in augment.columns if c != "geometry"]
    result = df.copy()
    df = df.copy()

    within = df.sjoin(
        augment,
        how="inner",
        predicate="within",
    )
    within_map = within["index_right"]
    df.drop(within.index, inplace=True)

    contained = df.sjoin(
        augment,
        how="inner",
        predicate="contains",
    )

    contained_map = contained["index_right"]
    df.drop(contained.index, inplace=True)

    # "Touches" means the boundaries touch but the interiors do not.
    # Touch is a case of intersect, but we don't care about it,
    # so we need to identify the touching pairs and then anti-join them away.
    touches = df.sjoin(
        augment,
        how="inner",
        predicate="touches",
    )

    # This yields any contact between the remaining elements.
    intersects = df.sjoin(
        augment,
        how="inner",
        predicate="intersects",
    )

    # Ignore pairs that are only touching
    touches.set_index("index_right", append=True, inplace=True)
    intersects.set_index("index_right", append=True, inplace=True)
    intersects = (
        intersects.join(pd.DataFrame(1, touches.index, ["_dummy"]), how="left")
        .query("_dummy != _dummy")
        .drop(columns="_dummy")
        .reset_index("index_right")
    )

    df.drop(intersects.index, inplace=True)

    # Find the most likely assignment of each row of `df` to a row of `augment`
    # by finding the pair that has the largest overlap area.
    with warnings.catch_warnings():
        # Gleefully ignore trivialities like the curvature of the earth
        warnings.filterwarnings(
            "ignore", r"Geometry is in a geographic CRS", UserWarning
        )
        intersects["_intersection_fraction"] = (
            intersects.intersection(
                augment.loc[intersects.index_right], align=False
            ).area.values
            / intersects.area.values
        )

    intersection_report = {}
    for name, group in intersects.groupby(level=0):
        intersection_report[name] = pd.Series(
            group["_intersection_fraction"].values, group["index_right"].values
        ).sort_values(ascending=False)

    intersects["_intersection_rank"] = intersects.groupby(level=0)[
        "_intersection_fraction"
    ].rank(method="first", ascending=False)
    intersects = intersects.loc[intersects["_intersection_rank"] == 1, keep_columns]
    assert intersects.index.is_unique

    result.loc[:, keep_columns] = pd.concat([within, contained, intersects])[
        keep_columns
    ]

    return OverlayResult(
        within=within_map,
        contained=contained_map,
        intersected=intersection_report,
        no_match=df.index,
        overlaid=result,
    )
