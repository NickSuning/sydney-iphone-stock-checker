"""Two stock checks per GitHub Actions run, 150 seconds apart, around the clock."""
import time

import stock_monitor

CHECK_INTERVAL_SECONDS = 150
CHECKS_PER_RUN = 2


def run_checks(check=None, monotonic=None, sleep=None):
    """Perform both checks, retaining the on-disk deduplication state.

    A failed first check does not prevent a second check. The GitHub runner
    persists the state file after the second check.
    """
    check = check or stock_monitor.main
    monotonic = monotonic or time.monotonic
    sleep = sleep or time.sleep
    start = monotonic()
    succeeded = False
    for index in range(CHECKS_PER_RUN):
        wait = start + index * CHECK_INTERVAL_SECONDS - monotonic()
        if wait > 0:
            sleep(wait)
        print(stock_monitor.timestamp(), f"Check {index + 1}/{CHECKS_PER_RUN}", flush=True)
        try:
            result = check()
            succeeded = (result == 0) or succeeded
            if result != 0:
                print(f"Check {index + 1} returned status {result}; continuing", flush=True)
        except Exception as exc:
            print(f"Check {index + 1} failed ({type(exc).__name__}); continuing", flush=True)
    return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(run_checks())
