"""Regression tests for two checks 150 seconds apart, day and night."""
import unittest
from unittest.mock import Mock
import poll_stock

class Clock:
    def __init__(self):
        self.seconds = 0
    def monotonic(self):
        return self.seconds
    def sleep(self, seconds):
        self.seconds += seconds

class PollTests(unittest.TestCase):
    def test_two_checks_at_150_second_intervals(self):
        clock = Clock()
        observed = []
        def check():
            observed.append(clock.seconds)
            return 0
        self.assertEqual(poll_stock.run_checks(check, clock.monotonic, clock.sleep), 0)
        self.assertEqual(observed, [0, 150])

    def test_runs_overnight_without_cutoff(self):
        clock = Clock()
        check = Mock(return_value=0)
        self.assertEqual(poll_stock.run_checks(check, clock.monotonic, clock.sleep), 0)
        self.assertEqual(check.call_count, 2)
        self.assertEqual(clock.seconds, 150)

    def test_recovers_from_error(self):
        clock = Clock()
        check = Mock(side_effect=[RuntimeError("transient"), 0])
        self.assertEqual(poll_stock.run_checks(check, clock.monotonic, clock.sleep), 0)
        self.assertEqual(check.call_count, 2)

    def test_nonzero_first_check_does_not_stop_second(self):
        clock = Clock()
        check = Mock(side_effect=[1, 0])
        self.assertEqual(poll_stock.run_checks(check, clock.monotonic, clock.sleep), 0)
        self.assertEqual(check.call_count, 2)

    def test_both_checks_fail(self):
        clock = Clock()
        check = Mock(return_value=1)
        self.assertEqual(poll_stock.run_checks(check, clock.monotonic, clock.sleep), 1)
        self.assertEqual(check.call_count, 2)

if __name__ == "__main__":
    unittest.main()
