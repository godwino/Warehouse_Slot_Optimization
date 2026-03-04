"""Slotting engine with random and PRIME slotting strategies."""

from __future__ import annotations

import numpy as np
import pandas as pd


VELOCITY_RANK = {"A": 0, "B": 1, "C": 2}


def assign_random_slotting(
    skus_df: pd.DataFrame, layout_df: pd.DataFrame, seed: int = 42
) -> pd.DataFrame:
    """Assign SKUs to random storage locations."""
    if len(layout_df) < len(skus_df):
        raise ValueError("Layout capacity is smaller than SKU count.")

    rng = np.random.default_rng(seed + 2)
    location_idx = rng.choice(layout_df.index.to_numpy(), size=len(skus_df), replace=False)
    assigned_locations = layout_df.loc[location_idx].reset_index(drop=True)
    assigned_skus = skus_df.sample(frac=1.0, random_state=seed + 3).reset_index(drop=True)

    slotted = pd.concat([assigned_skus, assigned_locations], axis=1)
    slotted["slotting_strategy"] = "Random"
    return slotted


def assign_prime_slotting(
    skus_df: pd.DataFrame,
    layout_df: pd.DataFrame,
    seed: int = 42,
) -> pd.DataFrame:
    """
    PRIME slotting:
    1) Rank SKUs by velocity and annual demand (high to low).
    2) Rank locations by ergonomic level first, then shortest travel distance.
    3) Pair best SKUs with best slots.
    """
    if len(layout_df) < len(skus_df):
        raise ValueError("Layout capacity is smaller than SKU count.")

    # Small random noise keeps ties from being deterministic blocks.
    rng = np.random.default_rng(seed + 4)
    sku_ranked = skus_df.copy()
    sku_ranked["velocity_rank"] = sku_ranked["velocity_class"].map(VELOCITY_RANK)
    sku_ranked["tie_break"] = rng.random(len(sku_ranked))
    sku_ranked = sku_ranked.sort_values(
        ["velocity_rank", "annual_demand", "tie_break"],
        ascending=[True, False, True],
    ).reset_index(drop=True)

    location_ranked = layout_df.copy()
    location_ranked["tie_break"] = rng.random(len(location_ranked))
    location_ranked = location_ranked.sort_values(
        ["ergonomic_level", "distance_to_pick_path_m", "tie_break"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    slotted = pd.concat(
        [sku_ranked.drop(columns=["velocity_rank", "tie_break"]), location_ranked.iloc[: len(sku_ranked)]],
        axis=1,
    )
    slotted["slotting_strategy"] = "Prime"
    return slotted
