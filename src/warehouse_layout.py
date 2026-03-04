"""Warehouse layout generation and travel distance geometry."""

from __future__ import annotations

import pandas as pd


def generate_layout(
    num_aisles: int = 20,
    bays_per_aisle: int = 30,
    levels: int = 4,
    aisle_spacing_m: float = 3.2,
    bay_spacing_m: float = 1.2,
) -> pd.DataFrame:
    """Create a location master with coordinates and distance to pick path."""
    rows: list[dict] = []
    for aisle in range(1, num_aisles + 1):
        x = aisle * aisle_spacing_m
        for bay in range(1, bays_per_aisle + 1):
            y = bay * bay_spacing_m
            # Manhattan distance from dock/pick path at origin (0,0).
            base_distance = abs(x) + abs(y)
            for level in range(1, levels + 1):
                location_id = f"A{aisle:03d}-B{bay:03d}-L{level}"
                rows.append(
                    {
                        "location_id": location_id,
                        "aisle": aisle,
                        "bay": bay,
                        "level": level,
                        "x_m": x,
                        "y_m": y,
                        "distance_to_pick_path_m": round(base_distance, 2),
                        "ergonomic_level": level in (2, 3),
                    }
                )

    return pd.DataFrame(rows)
