"""Three best-effort checks per GitHub Actions run, two minutes apart.

The GitHub cron launches one run every six minutes. Every check is gated by
Sydney local time, including manual dispatches and delayed jobs.
"""
from datetime import datetime
import time
from zoneinfo import ZoneInfo

import stock_monitor

SYDNEY_TZ = ZoneInfo("Australia/Sydney")
CHECK_INTERVAL_SECONDS = 120
CHECKS_PER_RUN = 3
START_HOUR = 7
END_HOUR = 22


def in_operating_window(current):
    local = current.astimezone(SYDNEY_TZ)
    return START_HOUR <= local.hour < END_HOUR


def run_checks(check=None, now=None, monotonic=None, sleep=None):
    """Poll at most three times; individual errors do not stop later polls.

    Consecutive checks share a local alert state file; the GitHub workflow
    commits that file once the runner finishes.
    """
    check = check or stock_monitor.main
    now = now or (lambda: datetime.now(SYDNEY_TZ))
    monotonic = monotonic or time.monotonic
    sleep = sleep or time.sleep
    start = monotonic()
    succeeded = False
    attempted = False
    for index in range(CHECKS_PER_RUN):
        wait = start + index * CHECK_INTERVAL_SECONDS - monotonic()
        if wait > 0:
            sleep(wait)
        when = now()
        if not in_operating_window(when):
            print(f"Skipping remaining checks outside 07:00-22:00 Sydney time: {when.isoformat()}", flush=True)
            break
        attempted = True
        print(f"Check {index + 1}/{CHECKS_PER_RUN} at {when.isoformat()}", flush=True)
        try:
            result = check()
            succeeded = (result == 0) or succeeded
            if result != 0:
                print(f"Check {index + 1} returned status {result}; continuing", flush=True)
        except Exception as exc:
            print(f"Check {index + 1} failed ({type(exc).__name__}); continuing", flush=True)
    return 0 if succeeded or not attempted else 1


if __name__ == "__main__":
    raise SystemExit(run_checks())
