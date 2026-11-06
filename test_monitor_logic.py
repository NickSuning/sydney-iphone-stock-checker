"""Offline regression tests for independent-store notifications and deduplication."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import stock_monitor
from stock_check import PickupResult


def item(name, status):
    return PickupResult(name, "R001", status)


class StockMonitorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "state.json"
        patcher = patch.object(stock_monitor, "STATE_FILE", self.state)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_chatswood_alert_even_if_other_stores_missing(self):
        results = {"Chatswood Chase": item("Chatswood Chase", "available")}
        with patch.object(stock_monitor, "collect", return_value=(results, ["Postcode 2750: HTTP 541"])), \
             patch.object(stock_monitor, "send_alert") as alert:
            self.assertEqual(stock_monitor.main(), 0)
            alert.assert_called_once()
            self.assertEqual(alert.call_args.args[0][0].store, "Chatswood Chase")
        self.assertEqual(stock_monitor.read_state(), {"Chatswood Chase"})

    def test_repeated_stock_does_not_email_twice(self):
        results = {"Chatswood Chase": item("Chatswood Chase", "available")}
        with patch.object(stock_monitor, "collect", return_value=(results, [])), \
             patch.object(stock_monitor, "send_alert") as alert:
            self.assertEqual(stock_monitor.main(), 0)
            self.assertEqual(stock_monitor.main(), 0)
            self.assertEqual(alert.call_count, 1)

    def test_missing_store_does_not_clear_last_alert(self):
        self.state.write_text(json.dumps({"alerted_stores": ["Chatswood Chase"]}))
        with patch.object(stock_monitor, "collect", return_value=({}, ["HTTP 541"])), \
             patch.object(stock_monitor, "send_alert") as alert:
            self.assertEqual(stock_monitor.main(), 1)
            alert.assert_not_called()
        self.assertEqual(stock_monitor.read_state(), {"Chatswood Chase"})

    def test_wrong_stock_state_never_alerts(self):
        results = {"Chatswood Chase": item("Chatswood Chase", "unavailable")}
        with patch.object(stock_monitor, "collect", return_value=(results, [])), \
             patch.object(stock_monitor, "send_alert") as alert:
            self.assertEqual(stock_monitor.main(), 0)
            alert.assert_not_called()

    def test_failed_email_not_marked_as_alerted(self):
        results = {"Chatswood Chase": item("Chatswood Chase", "available")}
        with patch.object(stock_monitor, "collect", return_value=(results, [])), \
             patch.object(stock_monitor, "send_alert", side_effect=RuntimeError("SMTP failed")):
            with self.assertRaises(RuntimeError):
                stock_monitor.main()
        self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
