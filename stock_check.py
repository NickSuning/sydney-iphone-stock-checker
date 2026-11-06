"""Strict parser for Apple Australia's pickup response.

No email notifications or background schedule are enabled by this module.
"""
from dataclasses import dataclass

PART_NUMBER = "MK2E4X/A"
# Accept only these seven official Greater Sydney store names.
SYDNEY_STORES = frozenset({
    "Sydney", "Broadway", "Bondi", "Chatswood Chase", "Miranda", "Castle Towers", "Penrith",
})

@dataclass(frozen=True)
class PickupResult:
    store: str
    store_number: str
    pickup_display: str

def parse_pickup(data: object) -> list[PickupResult]:
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object")
    body = data.get("body")
    if not isinstance(body, dict) or not isinstance(body.get("stores"), list):
        raise ValueError("Pickup stores array missing")
    results = []
    for store in body["stores"]:
        if not isinstance(store, dict):
            continue
        name = store.get("storeName")
        if name not in SYDNEY_STORES:
            continue
        number = store.get("storeNumber")
        parts = store.get("partsAvailability")
        availability = parts.get(PART_NUMBER) if isinstance(parts, dict) else None
        if not isinstance(number, str) or not number or not isinstance(availability, dict):
            raise ValueError("Missing store ID or exact SKU for " + name)
        status = availability.get("pickupDisplay")
        if status not in {"available", "unavailable", "ineligible"}:
            raise ValueError("Unknown pickup state for " + name)
        results.append(PickupResult(name, number, status))
    if not results:
        raise ValueError("No verified Sydney store entries found")
    if len({r.store for r in results}) != len(results):
        raise ValueError("Duplicate store entries")
    return results

def available_stores(data: object) -> list[PickupResult]:
    return [item for item in parse_pickup(data) if item.pickup_display == "available"]
