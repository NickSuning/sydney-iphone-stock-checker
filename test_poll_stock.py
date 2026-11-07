"""Offline tests of the polling cadence and Sydney operating window."""
import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from unittest.mock import Mock
import poll_stock

SYDNEY = ZoneInfo("Australia/Sydney")

class Clock:
    def __init__(self, start):
        self.start = start
        self.seconds = 0.0
    def now(self):
        return self.start + timedelta(seconds=self.seconds)
    def monotonic(self):
        return self.seconds
    def sleep(self, seconds):
        self.seconds += seconds

class PollTests(unittest.TestCase):
    def test_two_checks_at_150_second_intervals(self):
        clock = Clock(datetime(2026, 11, 7, 9, 0, tzinfo=SYDNEY))
        observed = []
        def check():
            observed.append(clock.seconds)
            return 0
        self.assertEqual(poll_stock.run_checks(check, clock.now, clock.monotonic, clock.sleep), 0)
        self.assertEqual(observed, [0, 150])

    def test_before_start_has_no_checks(self):
        clock = Clock(datetime(2026, 11, 7, 6, 59, tzinfo=SYDNEY))
        check = Mock(return_value=0)
        self.assertEqual(poll_stock.run_checks(check, clock.now, clock.monotonic, clock.sleep), 0)
        check.assert_not_called()

    def test_never_checks_after_ten_pm(self):
        clock = Clock(datetime(2026, 11, 7, 21, 57, tzinfo=SYDNEY))
        observed = []
        def check():
            observed.append(clock.seconds)
            return 0
        self.assertEqual(poll_stock.run_checks(check, clock.now, clock.monotonic, clock.sleep), 0)
        self.assertEqual(observed, [0, 150])

    def test_late_evening_second_check_is_skipped(self):
        clock = Clock(datetime(2026, 11, 7, 21, 58, tzinfo=SYDNEY))
        observed = []
        def check():
            observed.append(clock.seconds)
            return 0
        self.assertEqual(poll_stock.run_checks(check, clock.now, clock.monotonic, clock.sleep), 0)
        self.assertEqual(observed, [0])

    def test_error_recovery(self):
        clock = Clock(datetime(2026, 11, 7, 11, 0, tzinfo=SYDNEY))
        check = Mock(side_effect=[RuntimeError("simulated error"), 0])
        self.assertEqual(poll_stock.run_checks(check, clock.now, clock.monotonic, clock.sleep), 0)
        self.assertEqual(check.call_count, 2)

    def test_all_checks_fail(self):
        clock = Clock(datetime(2026, 11, 7, 11, 0, tzinfo=SYDNEY))
        check = Mock(return_value=1)
        self.assertEqual(poll_stock.run_checks(check, clock.now, clock.monotonic, clock.sleep), 1)
        self.assertEqual(check.call_count, 3)

    def test_dst_timezone(self):
        self.assertTrue(poll_stock.in_operating_window(datetime(2026, 7, 1, 0, 0, tzinfo=timezone.utc)))
        self.assertFalse(poll_stock.in_operating_window(datetime(2026, 7, 1, 12, 30, tzinfo=timezone.utc)))
        self.assertTrue(poll_stock.in_operating_window(datetime(2026, 11, 7, 0, 0, tzinfo=timezone.utc)))

if __name__ == "__main__":
    unittest.main()
