import unittest

from src.generate_data import generate_orders, generate_skus


class TestGenerateData(unittest.TestCase):
    def test_generate_skus_shape_and_columns(self):
        skus = generate_skus(num_skus=1000, seed=42)
        self.assertEqual(len(skus), 1000)
        self.assertIn("sku_id", skus.columns)
        self.assertIn("velocity_class", skus.columns)
        self.assertTrue(skus["sku_id"].is_unique)

    def test_generate_orders_basic_integrity(self):
        skus = generate_skus(num_skus=200, seed=123)
        orders = generate_orders(skus_df=skus, num_orders=100, seed=123)
        self.assertGreater(len(orders), 0)
        self.assertEqual(orders["order_id"].nunique(), 100)
        self.assertTrue(orders["sku_id"].isin(skus["sku_id"]).all())
        self.assertTrue((orders["qty"] > 0).all())


if __name__ == "__main__":
    unittest.main()
