"""Inbound truck arrival simulation."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def simulate_truck_arrivals(
    skus_df: pd.DataFrame,
    num_trucks: int = 100,
    min_skus_per_truck: int = 20,
    max_skus_per_truck: int = 80,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate truck arrivals and their inbound SKU cases."""
    rng = np.random.default_rng(seed + 5)
    sku_ids = skus_df["sku_id"].to_numpy()

    start_ts = datetime(2026, 1, 1, 6, 0, 0)
    rows: list[dict] = []

    for t in range(1, num_trucks + 1):
        truck_id = f"TRK-{t:03d}"
        arrival_time = start_ts + timedelta(minutes=int(rng.integers(0, 16 * 60)))
        sku_count = int(
            rng.integers(min_skus_per_truck, min(max_skus_per_truck, len(sku_ids)) + 1)
        )
        truck_skus = rng.choice(sku_ids, size=sku_count, replace=False)
        cases = rng.integers(1, 65, size=sku_count)

        for sku_id, qty in zip(truck_skus, cases):
            rows.append(
                {
                    "truck_id": truck_id,
                    "arrival_time": arrival_time,
                    "sku_id": sku_id,
                    "cases": int(qty),
                }
            )

    return pd.DataFrame(rows).sort_values(["arrival_time", "truck_id"]).reset_index(drop=True)
