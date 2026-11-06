"""Offline tests of checkout-handoff alert content, without sending mail."""
import unittest
from unittest.mock import patch
import stock_monitor
from stock_check import PickupResult

class FakeSMTP:
    messages = []
    def __init__(self, *args, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def login(self, sender, password):
        self.sender = sender
    def send_message(self, msg):
        self.messages.append(msg)

class AlertContentTests(unittest.TestCase):
    def setUp(self):
        FakeSMTP.messages = []
    def test_available_exact_sku_alert_contains_store_and_link(self):
        item = PickupResult("Chatswood Chase", "R123", "available")
        with patch.dict("os.environ", {"GMAIL_ADDRESS": "nickysuning@gmail.com",
                                       "GMAIL_APP_PASSWORD": "fake-test-only"}), \
             patch.object(stock_monitor.smtplib, "SMTP_SSL", FakeSMTP):
            stock_monitor.send_alert([item])
        self.assertEqual(len(FakeSMTP.messages), 1)
        msg = FakeSMTP.messages[0]
        self.assertIn("Chatswood Chase", msg["Subject"])
        plain = msg.get_body(preferencelist=("plain",)).get_content()
        html = msg.get_body(preferencelist=("html",)).get_content()
        self.assertIn(stock_monitor.PART_NUMBER, plain)
        self.assertIn(stock_monitor.APPLE_PRODUCT_URL, plain)
        self.assertIn("Open Apple product page", html)
        self.assertIn("does not reserve stock", plain)
    def test_non_available_cannot_send(self):
        with self.assertRaises(ValueError), patch.dict("os.environ", {
            "GMAIL_ADDRESS": "nickysuning@gmail.com", "GMAIL_APP_PASSWORD": "fake"
        }):
            stock_monitor.send_alert([PickupResult("Sydney", "R001", "unavailable")])

if __name__ == "__main__":
    unittest.main()
