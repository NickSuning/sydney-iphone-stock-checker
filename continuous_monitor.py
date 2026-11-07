"""Always-on Apple pickup monitoring loop for a persistent server.

Runs without cron or GitHub Actions scheduling. The process is intended to
be supervised by systemd, which restarts it after machine boots or crashes.
"""
import logging
import signal
import time

import stock_monitor

INTERVAL_SECONDS = 150
_stop = False


def stop_handler(signum, frame):
    global _stop
    _stop = True


def run_forever(check=None, clock=None, sleep=None):
    global _stop
    check = check or stock_monitor.main
    clock = clock or time.monotonic
    sleep = sleep or time.sleep
    next_check = clock()
    while not _stop:
        wait = next_check - clock()
        if wait > 0:
            sleep(min(wait, 1))  # responsive to SIGTERM
            continue
        try:
            result = check()
            if result != 0:
                logging.warning("Stock-check returned %s; next check remains scheduled", result)
        except Exception:
            logging.exception("Stock-check error; monitoring will continue")
        # Space checks >= 150 seconds from their actual start, without
        # bursts after slow calls or downtime.
        next_check = max(next_check + INTERVAL_SECONDS, clock() + 1)
    logging.info("Monitoring stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    logging.info("Starting continuous 24/7 monitoring with %ss interval", INTERVAL_SECONDS)
    run_forever()
