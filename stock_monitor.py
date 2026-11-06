"""Exact-SKU Apple pickup monitor with independent store alerts and audit logs."""
import json
import os
from pathlib import Path
import smtplib
import sys
from email.message import EmailMessage
from stock_check import PART_NUMBER, SYDNEY_STORES
from validate_pickup import collect, timestamp, print_status

STATE_FILE = Path(".stock_alert_state.json")
APPLE_PRODUCT_URL = "https://www.apple.com/au/shop/buy-iphone/iphone-duo/7.6-inch-display-256gb-night-sky"
SENDER = "nickysuning@gmail.com"
RECIPIENT = "nickysu@126.com"

def read_state():
    if not STATE_FILE.exists():
        return set()
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    names = data.get("alerted_stores") if isinstance(data, dict) else None
    if not isinstance(names, list) or any(
        not isinstance(name, str) or name not in SYDNEY_STORES for name in names
    ):
        raise ValueError("Invalid alert state file")
    return set(names)

def save_state(alerted):
    STATE_FILE.write_text(
        json.dumps({"alerted_stores": sorted(alerted)}, indent=2) + "\n", encoding="utf-8"
    )

def send_alert(stores):
    sender = os.environ.get("GMAIL_ADDRESS", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if sender != SENDER or not password:
        raise RuntimeError("Gmail configuration missing or unexpected sender")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = RECIPIENT
    msg["Subject"] = "Apple pickup available: iPhone Duo 256GB Night Sky — Greater Sydney"
    details = "\n".join(
        f"- Apple {item.store} (store ID {item.store_number})" for item in stores
    )
    msg.set_content(
        f"Verified pickup response for exact part {PART_NUMBER} "
        "(iPhone Duo 256GB Night Sky) at:\n\n"
        + details + "\n\nOfficial Apple product page:\n"
        + APPLE_PRODUCT_URL
        + "\n\nConfirm pickup and product configuration in Apple's checkout. "
        "Availability can change rapidly.\n"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
    print(timestamp(), "email accepted for", ", ".join(x.store for x in stores))

def main():
    print(timestamp(), "START pickup check; exact SKU", PART_NUMBER, flush=True)
    current, issues = collect()
    print_status(current, issues)
    previous = read_state()
    # Missing stores retain previous state: transient errors must not reset
    # deduplication and cause spurious repeated alerts on recovery.
    next_state = set(previous)
    for name, item in current.items():
        if item.pickup_display == "available":
            next_state.add(name)
        else:
            next_state.discard(name)
    new = sorted(
        name for name, item in current.items()
        if item.pickup_display == "available" and name not in previous
    )
    print(timestamp(), "new qualifying stores:", ", ".join(new) or "none")
    if new:
        send_alert([current[name] for name in new])
    if next_state != previous:
        save_state(next_state)
    missing = SYDNEY_STORES - current.keys()
    if missing:
        print(timestamp(), "unverified stores:", ", ".join(sorted(missing)), file=sys.stderr)
    print(timestamp(), "END check", len(current), "of", len(SYDNEY_STORES), "verified")
    # Missing/failed stores are reported, but do not suppress independently verified alerts.
    return 0 if current else 1

if __name__ == "__main__":
    raise SystemExit(main())
