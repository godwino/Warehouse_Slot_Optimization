import unittest

from src.generate_data import generate_orders, generate_skus
from src.picking_simulation import build_travel_heatmap_data, simulate_picking
from src.slotting_engine import assign_prime_slotting
from src.truck_simulation import simulate_truck_arrivals
from src.warehouse_layout import generate_layout


class TestPickingAndTrucks(unittest.TestCase):
    def test_picking_returns_positive_distance(self):
        skus = generate_skus(num_skus=500, seed=99)
        orders = generate_orders(skus_df=skus, num_orders=200, seed=99)
        layout = generate_layout(num_aisles=20, bays_per_aisle=20, levels=4)
        slotting = assign_prime_slotting(skus, layout, seed=99)
        metrics, picks = simulate_picking(orders, slotting)

        self.assertGreater(metrics["total_travel_distance_m"], 0)
        self.assertGreater(metrics["cases_picked"], 0)
        self.assertEqual(metrics["order_lines"], len(picks))

        heatmap = build_travel_heatmap_data(picks)
        self.assertGreater(len(heatmap), 0)
        self.assertIn("visit_count", heatmap.columns)

    def test_truck_simulation_count(self):
        skus = generate_skus(num_skus=1000, seed=42)
        trucks = simulate_truck_arrivals(skus_df=skus, num_trucks=100, seed=42)
        self.assertEqual(trucks["truck_id"].nunique(), 100)
        self.assertTrue((trucks["cases"] >= 1).all())


if __name__ == "__main__":
    unittest.main()
