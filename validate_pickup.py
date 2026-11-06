"""Read-only diagnostic for an *unverified* Apple Australia pickup endpoint.

Never interprets a failed or ambiguous response as stock availability.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

PART_NUMBER = "MK2E4X/A"  # Candidate only: verify against Apple AU first.
POSTCODE = "2000"

def main():
    query = urllib.parse.urlencode({"parts.0": PART_NUMBER, "location": POSTCODE})
    url = "https://www.apple.com/au/shop/fulfillment-messages?" + query
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.load(response)
            print("HTTP:", response.status)
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        print("Endpoint not verified:", type(exc).__name__, "HTTP status:", getattr(exc, "code", "n/a"), file=sys.stderr)
        return 1
    body = payload.get("body", {}) if isinstance(payload, dict) else {}
    content = body.get("content", {}) if isinstance(body, dict) else {}
    pickup = content.get("pickupMessage", {}) if isinstance(content, dict) else {}
    stores = pickup.get("stores", []) if isinstance(pickup, dict) else []
    print("JSON returned; pickup store count:", len(stores) if isinstance(stores, list) else "invalid")
    if not isinstance(stores, list) or not stores:
        print("Pickup structure not validated; no stock determination.")
        return 1
    for store in stores:
        if not isinstance(store, dict):
            continue
        name = store.get("storeName", "(unknown)")
        parts = store.get("partsAvailability", {})
        item = parts.get(PART_NUMBER, {}) if isinstance(parts, dict) else {}
        print("Store:", name, "| SKU entry present:", bool(item),
              "| pickupDisplay:", item.get("pickupDisplay", "(missing)") if isinstance(item, dict) else "(invalid)")
    print("Diagnostic only: no notifications, no availability claims.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
