import unittest

from src.generate_data import generate_skus
from src.slotting_engine import assign_prime_slotting, assign_random_slotting
from src.warehouse_layout import generate_layout


class TestLayoutAndSlotting(unittest.TestCase):
    def test_layout_capacity(self):
        layout = generate_layout(num_aisles=10, bays_per_aisle=10, levels=4)
        self.assertEqual(len(layout), 400)
        self.assertIn("distance_to_pick_path_m", layout.columns)

    def test_slotting_assignments_cover_all_skus(self):
        skus = generate_skus(num_skus=300, seed=7)
        layout = generate_layout(num_aisles=10, bays_per_aisle=10, levels=4)
        random_slotting = assign_random_slotting(skus, layout, seed=7)
        prime_slotting = assign_prime_slotting(skus, layout, seed=7)

        self.assertEqual(len(random_slotting), len(skus))
        self.assertEqual(len(prime_slotting), len(skus))
        self.assertEqual(random_slotting["location_id"].nunique(), len(skus))
        self.assertEqual(prime_slotting["location_id"].nunique(), len(skus))
        self.assertSetEqual(set(random_slotting["sku_id"]), set(skus["sku_id"]))
        self.assertSetEqual(set(prime_slotting["sku_id"]), set(skus["sku_id"]))


if __name__ == "__main__":
    unittest.main()
