"""Greater Sydney Apple pickup diagnostic. Read-only; never sends alerts.

Queries multiple postcodes because Apple limits the returned stores by proximity.
Failure to retrieve all six locations results in nonzero exit status.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from stock_check import PART_NUMBER, SYDNEY_STORES, parse_pickup

POSTCODES = ("2000", "2067", "2228", "2154")
ENDPOINT = "https://www.apple.com/au/shop/retail/pickup-message"


def fetch(postcode):
    params = urllib.parse.urlencode({
        "pl": "true",
        "mts.0": "regular",
        "parts.0": PART_NUMBER,
        "location": postcode,
    })
    request = urllib.request.Request(
        ENDPOINT + "?" + params,
        headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print("Postcode", postcode, "HTTP", response.status, flush=True)
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Postcode {postcode}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, ValueError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Postcode {postcode}: {type(exc).__name__}") from exc


def collect():
    matched = {}
    failed = []
    for i, postcode in enumerate(POSTCODES):
        if i:
            time.sleep(1)
        try:
            for result in parse_pickup(fetch(postcode)):
                prior = matched.get(result.store)
                if prior and (
                    prior.store_number != result.store_number
                    or prior.pickup_display != result.pickup_display
                ):
                    failed.append(f"Conflicting results for {result.store}")
                else:
                    matched[result.store] = result
        except (RuntimeError, ValueError) as exc:
            failed.append(str(exc))
    return matched, failed


def main():
    print("Apple pickup diagnostic: candidate AU part", PART_NUMBER)
    matched, errors = collect()
    for name in sorted(SYDNEY_STORES):
        result = matched.get(name)
        print(name, ":", (result.pickup_display + " | " + result.store_number) if result else "NOT RETURNED")
    if errors:
        print("Errors:", "; ".join(errors), file=sys.stderr)
    missing = SYDNEY_STORES - matched.keys()
    if missing:
        print("Coverage incomplete:", ", ".join(sorted(missing)), file=sys.stderr)
    if errors or missing:
        print("Diagnostic failed closed: do not enable alerts.")
        return 1
    print("Six-store response coverage validated for candidate SKU.")
    print("SKU identity and actual customer checkout still require independent verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
