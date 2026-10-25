"""Picker travel simulation for outbound orders."""

from __future__ import annotations

import pandas as pd


def simulate_picking(
    orders_df: pd.DataFrame,
    slotting_df: pd.DataFrame,
    walking_speed_mps: float = 1.4,
    handling_seconds_per_case: float = 4.0,
) -> tuple[dict, pd.DataFrame]:
    """
    Simulate order picking.
    Legacy geometry: each order follows aisle/bay order, returning to the front cross-aisle after each visited aisle. Illustrative, not calibrated.
    """
    if walking_speed_mps <= 0 or handling_seconds_per_case < 0:
        raise ValueError('Invalid timing assumptions')
    if not orders_df['sku_id'].isin(slotting_df['sku_id']).all():
        raise ValueError('Unknown order SKU; no lines may be dropped')
    picks = orders_df.merge(
        slotting_df[
            [
                "sku_id",
                "location_id",
                "aisle",
                "bay",
                "level",
                "x_m",
                "y_m",
                "distance_to_pick_path_m",
                "slotting_strategy",
            ]
        ],
        on="sku_id",
        how="inner",
    )

    if picks.empty:
        return (
            {
                "slotting_strategy": "Unknown",
                "total_travel_distance_m": 0.0,
                "cases_picked": 0,
                "cases_per_hour": 0.0,
                "order_lines": 0,
            },
            picks,
        )

    picks = picks.sort_values(['order_id','aisle','bay','level']).copy()
    picks['line_distance_m'] = 0.0
    for _, group in picks.groupby('order_id'):
        distance = 2 * group['x_m'].max()
        distance += sum(2 * aisle['y_m'].max() for _, aisle in group.groupby('aisle'))
        picks.loc[group.index[0], 'line_distance_m'] = distance
    total_distance = float(picks["line_distance_m"].sum())
    cases_picked = int(picks["qty"].sum())
    travel_seconds = total_distance / walking_speed_mps
    handling_seconds = cases_picked * handling_seconds_per_case
    total_hours = (travel_seconds + handling_seconds) / 3600.0
    cph = (cases_picked / total_hours) if total_hours > 0 else 0.0

    metrics = {
        "slotting_strategy": picks["slotting_strategy"].iloc[0],
        "total_travel_distance_m": round(total_distance, 2),
        "cases_picked": cases_picked,
        "cases_per_hour": round(cph, 2),
        "order_lines": int(len(picks)),
    }
    return metrics, picks


def build_travel_heatmap_data(picks_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate picker visits per aisle/bay for heatmap visualization."""
    if picks_df.empty:
        return pd.DataFrame(columns=["aisle", "bay", "visit_count", "distance_sum_m"])

    heatmap = (
        picks_df.groupby(["aisle", "bay"], as_index=False)
        .agg(
            visit_count=("order_id", "count"),
            distance_sum_m=("line_distance_m", "sum"),
        )
        .sort_values(["aisle", "bay"])
    )
    return heatmap
