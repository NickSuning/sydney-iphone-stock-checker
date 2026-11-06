"""Offline unit tests: no API or email access."""
import unittest
from stock_check import parse_pickup, available_stores, PART_NUMBER

def payload(state="available", name="Sydney", sku=PART_NUMBER):
    return {"body": {"stores": [{
        "storeName": name, "storeNumber": "R001",
        "partsAvailability": {sku: {"pickupDisplay": state}}
    }]}}

class StockParserTests(unittest.TestCase):
    def test_exact_sku_available(self):
        self.assertEqual([r.store for r in available_stores(payload())], ["Sydney"])
    def test_unavailable_not_alerted(self):
        self.assertEqual(available_stores(payload("unavailable")), [])
    def test_wrong_sku_not_alerted(self):
        with self.assertRaises(ValueError):
            available_stores(payload(sku="OTHER-SKU"))
    def test_non_sydney_store_not_alerted(self):
        with self.assertRaises(ValueError):
            available_stores(payload(name="Melbourne"))
    def test_unknown_state_not_alerted(self):
        with self.assertRaises(ValueError):
            available_stores(payload(state="unknown"))
    def test_malformed_response_not_alerted(self):
        with self.assertRaises(ValueError):
            available_stores({"body": {}})

if __name__ == "__main__":
    unittest.main()
