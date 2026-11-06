"""Read-only diagnostic of Apple's undocumented Australia retail pickup interface.

No scheduling, no notification and no conclusion from missing or rejected data.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

PART_NUMBER = "MK2E4X/A"  # Candidate Australian SKU; confirm against Apple catalogue.
POSTCODE = "2000"
ENDPOINT = "https://www.apple.com/au/shop/retail/pickup-message"
VALID_STATES = {"available", "unavailable", "ineligible"}

def main():
    params = urllib.parse.urlencode({
        "pl": "true",
        "mts.0": "regular",
        "parts.0": PART_NUMBER,
        "location": POSTCODE,
    })
    request = urllib.request.Request(
        ENDPOINT + "?" + params,
        headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    print("Endpoint:", ENDPOINT, "| postal code:", POSTCODE, "| candidate SKU:", PART_NUMBER)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.status
            data = json.load(response)
            print("HTTP status:", status)
    except urllib.error.HTTPError as exc:
        print("Endpoint rejected request: HTTP", exc.code, "(not an inventory result)", file=sys.stderr)
        return 1
    except (urllib.error.URLError, ValueError, TimeoutError, OSError) as exc:
        print("Endpoint not verified:", type(exc).__name__, "(not an inventory result)", file=sys.stderr)
        return 1

    if not isinstance(data, dict) or not isinstance(data.get("body"), dict):
        print("Unexpected response: missing body object", file=sys.stderr)
        return 1
    stores = data["body"].get("stores")
    if not isinstance(stores, list) or not stores:
        print("Unexpected response: no stores list", file=sys.stderr)
        return 1
    print("Stores returned:", len(stores))
    validated = 0
    for store in stores:
        if not isinstance(store, dict):
            continue
        parts = store.get("partsAvailability")
        item = parts.get(PART_NUMBER) if isinstance(parts, dict) else None
        state = item.get("pickupDisplay") if isinstance(item, dict) else None
        name = store.get("storeName", "(unnamed)")
        number = store.get("storeNumber", "(no store ID)")
        print("Store:", str(name)[:70], "| ID:", str(number)[:15], "| state:", state if state in VALID_STATES else "UNKNOWN")
        if state in VALID_STATES and name and number:
            validated += 1

    print("Stores with recognized candidate-SKU state:", validated, "/", len(stores))
    if validated == 0:
        print("Not validated: no recognized inventory states for candidate SKU", file=sys.stderr)
        return 1
    print("Diagnostic only. Do NOT interpret this as validation of SKU identity, complete Sydney coverage, or alerts.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
