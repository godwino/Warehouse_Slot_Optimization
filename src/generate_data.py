"""Synthetic data generation for the warehouse digital twin."""

from __future__ import annotations

import numpy as np
import pandas as pd


CATEGORIES = ["Dry Food", "Beverage", "Pet", "Chemical"]
VELOCITY_CLASSES = ["A", "B", "C"]
VELOCITY_PROBS = [0.2, 0.3, 0.5]


def generate_skus(num_skus: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate SKU master data with velocity, category, and dimensions."""
    rng = np.random.default_rng(seed)

    sku_ids = [f"SKU-{i:05d}" for i in range(1, num_skus + 1)]
    categories = rng.choice(CATEGORIES, size=num_skus, p=[0.45, 0.25, 0.2, 0.1])
    velocity_classes = rng.choice(VELOCITY_CLASSES, size=num_skus, p=VELOCITY_PROBS)

    # Higher baseline demand for faster movers.
    demand_by_velocity = {"A": (700, 1200), "B": (250, 650), "C": (60, 240)}
    annual_demand = np.array(
        [rng.integers(*demand_by_velocity[v]) for v in velocity_classes], dtype=int
    )

    weights = rng.uniform(0.3, 22.0, size=num_skus).round(2)
    length_cm = rng.uniform(10.0, 65.0, size=num_skus).round(1)
    width_cm = rng.uniform(8.0, 45.0, size=num_skus).round(1)
    height_cm = rng.uniform(5.0, 40.0, size=num_skus).round(1)
    cube_cm3 = (length_cm * width_cm * height_cm).round(1)

    return pd.DataFrame(
        {
            "sku_id": sku_ids,
            "category": categories,
            "velocity_class": velocity_classes,
            "annual_demand": annual_demand,
            "weight_kg": weights,
            "length_cm": length_cm,
            "width_cm": width_cm,
            "height_cm": height_cm,
            "cube_cm3": cube_cm3,
        }
    )


def generate_orders(
    skus_df: pd.DataFrame,
    num_orders: int = 500,
    min_lines_per_order: int = 1,
    max_lines_per_order: int = 6,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic outbound order lines, weighted by SKU velocity."""
    rng = np.random.default_rng(seed + 1)

    velocity_weight_map = {"A": 6.0, "B": 2.5, "C": 1.0}
    base_weights = skus_df["velocity_class"].map(velocity_weight_map).to_numpy(dtype=float)
    demand_weights = skus_df["annual_demand"].to_numpy(dtype=float)
    pick_weights = base_weights * (0.5 + demand_weights / demand_weights.max())
    pick_probs = pick_weights / pick_weights.sum()

    sku_ids = skus_df["sku_id"].to_numpy()
    order_rows: list[dict] = []

    for order_idx in range(1, num_orders + 1):
        order_id = f"ORD-{order_idx:05d}"
        line_count = int(rng.integers(min_lines_per_order, max_lines_per_order + 1))
        # Avoid duplicate SKU lines within a single order.
        selected_skus = rng.choice(
            sku_ids,
            size=min(line_count, len(sku_ids)),
            replace=False,
            p=pick_probs,
        )
        qtys = rng.integers(1, 9, size=len(selected_skus))
        for sku_id, qty in zip(selected_skus, qtys):
            order_rows.append({"order_id": order_id, "sku_id": sku_id, "qty": int(qty)})

    return pd.DataFrame(order_rows)
