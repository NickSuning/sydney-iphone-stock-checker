"""Apple AU pickup collector and diagnostic; timestamps use Sydney local time.

Failed postcode requests do not erase valid observations from other postcodes.
Conflicting observations for one store quarantine that store alone.
"""
import json
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import urllib.error
import urllib.parse
import urllib.request
from stock_check import PART_NUMBER, SYDNEY_STORES, parse_pickup

POSTCODES = ("2000", "2067", "2228", "2154", "2750")
ENDPOINT = "https://www.apple.com/au/shop/retail/pickup-message"
TIMEZONE = ZoneInfo("Australia/Sydney")

def timestamp():
    return datetime.now(TIMEZONE).isoformat(timespec="seconds")

def fetch(postcode):
    params = urllib.parse.urlencode({
        "pl": "true", "mts.0": "regular",
        "parts.0": PART_NUMBER, "location": postcode,
    })
    request = urllib.request.Request(
        ENDPOINT + "?" + params,
        headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print(timestamp(), "postcode", postcode, "HTTP", response.status, flush=True)
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Postcode {postcode}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, ValueError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Postcode {postcode}: {type(exc).__name__}") from exc

def collect():
    matched = {}
    conflicted = set()
    issues = []
    for i, postcode in enumerate(POSTCODES):
        if i:
            time.sleep(1)
        try:
            rows = parse_pickup(fetch(postcode))
        except (RuntimeError, ValueError) as exc:
            issues.append(str(exc))
            continue
        for item in rows:
            if item.store in conflicted:
                continue
            previous = matched.get(item.store)
            if previous and (previous.store_number != item.store_number or
                             previous.pickup_display != item.pickup_display):
                issues.append(f"Conflicting responses for {item.store}")
                matched.pop(item.store, None)
                conflicted.add(item.store)
            else:
                matched[item.store] = item
    return matched, issues

def print_status(matched, issues):
    for name in sorted(SYDNEY_STORES):
        item = matched.get(name)
        print(timestamp(), "store", name, "status",
              item.pickup_display if item else "UNKNOWN",
              "id", item.store_number if item else "n/a", flush=True)
    for issue in issues:
        print(timestamp(), "warning", issue, file=sys.stderr)

def main():
    print(timestamp(), "begin validation", PART_NUMBER)
    matched, issues = collect()
    print_status(matched, issues)
    missing = SYDNEY_STORES - matched.keys()
    if missing:
        print(timestamp(), "missing stores:", ", ".join(sorted(missing)), file=sys.stderr)
    print(timestamp(), "end validation", len(matched), "of", len(SYDNEY_STORES))
    return 1 if issues or missing else 0

if __name__ == "__main__":
    raise SystemExit(main())
