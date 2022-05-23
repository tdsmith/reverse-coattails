import warnings

import attr
import geopandas as gpd
import pandas as pd


@attr.define
class OverlayResult:
    within: pd.Series
    contained: pd.Series
    intersected: dict[str, pd.DataFrame]
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

    touches = df.sjoin(
        augment,
        how="inner",
        predicate="touches",
    )

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

    with warnings.catch_warnings():
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
