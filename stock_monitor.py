"""Monitor exact Apple AU pickup SKU in all seven Greater Sydney Apple Stores.

Only sends when the validated Apple pickup response reports 'available'.
Uses a git-tracked set of already-alerted stores so consecutive runs do not spam.
"""
import json
import os
from pathlib import Path
import smtplib
import sys
from email.message import EmailMessage

from stock_check import PART_NUMBER, SYDNEY_STORES
from validate_pickup import collect

STATE_FILE = Path(".stock_alert_state.json")
APPLE_PRODUCT_URL = (
    "https://www.apple.com/au/shop/buy-iphone/"
    "iphone-duo/7.6-inch-display-256gb-night-sky"
)
SENDER = "nickysuning@gmail.com"
RECIPIENT = "nickysu@126.com"


def read_state():
    if not STATE_FILE.exists():
        return set()
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("alerted_stores"), list):
        raise ValueError("Invalid alert state file")
    names = data["alerted_stores"]
    if any(not isinstance(name, str) or name not in SYDNEY_STORES for name in names):
        raise ValueError("Unexpected state entries")
    return set(names)


def save_state(alerted):
    STATE_FILE.write_text(
        json.dumps({"alerted_stores": sorted(alerted)}, indent=2) + "\n",
        encoding="utf-8",
    )


def send_alert(stores):
    sender = os.environ.get("GMAIL_ADDRESS", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if sender != SENDER or not password:
        raise RuntimeError("Gmail sender or app password secret unavailable")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = RECIPIENT
    msg["Subject"] = "Apple pickup available: iPhone Duo 256GB Night Sky — Greater Sydney"
    details = "\n".join(f"- Apple {result.store} (store ID {result.store_number})" for result in stores)
    msg.set_content(
        "Apple's pickup endpoint reported available for the exact Australian SKU "
        f"{PART_NUMBER} (iPhone Duo 256GB Night Sky) at:\n\n"
        f"{details}\n\n"
        "Purchase/check pickup directly through the official Apple product page:\n"
        f"{APPLE_PRODUCT_URL}\n\n"
        "Stock can change before you complete checkout. "
        "Confirm pickup at the selected store before travelling.\n"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
        server.login(sender, password)
        server.send_message(msg)
    print("Gmail accepted an availability alert for", len(stores), "store(s)")


def main():
    current, errors = collect()
    missing = SYDNEY_STORES - current.keys()
    if errors or missing:
        print("Stock check incomplete; no alerts or state changes.", file=sys.stderr)
        for error in errors:
            print("Error:", error, file=sys.stderr)
        if missing:
            print("Missing stores:", ", ".join(sorted(missing)), file=sys.stderr)
        return 1

    available = {name for name, item in current.items() if item.pickup_display == "available"}
    previous = read_state()
    new = available - previous
    print("Seven stores verified. Available:", ", ".join(sorted(available)) or "none")
    print("Newly available:", ", ".join(sorted(new)) or "none")
    if new:
        send_alert([current[name] for name in sorted(new)])
    # Save after successfully sending. GitHub workflow commits this file to persist state.
    if available != previous:
        save_state(available)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
