# Sydney iPhone Duo stock checker

**Status: 5-minute scheduled workflow committed. Alerts are fail-closed if the live Apple endpoint does not return all seven Greater Sydney stores with valid exact-SKU statuses.**

Target: Apple iPhone Duo 256GB Night Sky, Australian retailer part number `MK2E4X/A`.

Official purchase page: https://www.apple.com/au/shop/buy-iphone/iphone-duo/7.6-inch-display-256gb-night-sky

## Before enabling
1. Confirm Apple's live pickup JSON endpoint and that the part number is accepted. No assumption of availability from a third-party site.
2. Confirm the exact Sydney Apple Store IDs and verify the response maps the SKU to the right colour/capacity.
3. Add GitHub Actions secrets `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` (never commit credentials). Recipient is `nickysu@126.com`.
4. Test email delivery separately from stock alerts.
5. Only then add a 5-minute cron schedule. A scheduled GitHub Actions run may be delayed.

Sender: `nickysuning@gmail.com`. Do not publish or share the app password.

## Endpoint validation result (6 Nov 2026)
Manual GitHub Actions validation run `42171282621` returned HTTP **541** from the candidate Apple Australia `/au/shop/fulfillment-messages` endpoint. This is an unverified endpoint response, **not** evidence of inventory availability or unavailability. The SKU `MK2E4X/A` matches Australian retailer listings for the specified colour/capacity, but Apple pickup API support for this SKU and store locations remains unverified. Do not enable an unattended polling schedule or stock-alert email until a working and permitted inventory source has been tested, including a positive and negative response.

## Greater Sydney test coverage
The read-only workflow `validate.yml` now queries postcodes 2000, 2067, 2228 and 2154 and validates these six stores: Sydney, Broadway, Bondi, Chatswood Chase, Miranda and Castle Towers. If any store is missing, a response conflicts, or a postcode request fails, validation fails closed. A passing initial one-postcode run does not establish full coverage.

## Gmail delivery test
The `test-email.yml` workflow can be manually dispatched from GitHub Actions. It uses repository Actions secrets `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`, and sends **a clearly marked test message**, not an inventory alert, to `nickysu@126.com`. Confirm receipt and phone notification independently.

## Current deployment gate
Do **not** add a five-minute schedule or stock-available alerts until:
- Six-store multi-postcode validation passes.
- Exact-SKU identity and a positive and negative stock response are independently validated.
- SMTP delivery test succeeds.
- Deduplication/notification state and customer-facing Apple purchase link are tested.

## Scheduled monitor
The `.github/workflows/stock-monitor.yml` workflow runs every five minutes (best-effort GitHub scheduling). `stock_monitor.py` requests the Apple Australia pickup interface for postcodes 2000, 2067, 2228, 2154, 2750, requiring valid responses for every listed store: Sydney, Broadway, Bondi, Chatswood Chase, Miranda, Castle Towers, **Penrith**. Failure of any query, conflicting store status or missing store causes no stock alert.

When the exact candidate part number `MK2E4X/A` reports `pickupDisplay=available`, the script sends a Gmail email to `nickysu@126.com` identifying the store and linking to the exact Apple AU product page. The GitHub workflow commits `.stock_alert_state.json` only when the set of alerted stores changes, suppressing repeated alerts while availability remains unchanged. A store may alert again after it is observed unavailable and later reappears as available.

**Important:** The prior successful manual test was for a six-store list. The seven-store version, including Penrith, needs to be confirmed through workflow logs. Until full coverage works, the monitor deliberately does not email. A GitHub schedule is not an exact real-time 5-minute guarantee. Successful SMTP submission does not guarantee push delivery.

Security: GitHub Actions uses encrypted `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` repository secrets. No credentials belong in source control. 
