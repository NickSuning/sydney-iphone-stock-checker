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

## Reliability improvements — 7 November 2026
- **Independent store alerts:** A failed postcode request or missing store no longer suppresses a valid exact-SKU `available` response at another Sydney store. Contradictory responses for the same store quarantine *that store*, with no alert for it.
- **Sydney-time logs:** Each queried postcode and each of the seven store statuses is printed with an Australia/Sydney timestamp. Missing stores are explicitly `UNKNOWN`, never `unavailable`.
- **Deduplication:** If a store cannot be checked, its previous alerted state is retained, avoiding a duplicate email when the source recovers. Only a confirmed `unavailable` or `ineligible` observation resets that store.
- **Operating window:** 7:02 am to 9:57 pm Australia/Sydney (best-effort five-minute GitHub scheduling). Manual dispatch remains possible outside this window.
- **Regression tests:** Offline unit tests cover partial results, repeated positives, unknown stores and failed email attempts.

Note that a passing run does not prove Apple's checkout will hold an item until purchase. The exact Australian SKU association and Apple product URL should be reconfirmed against customer checkout when acting on an alert.

## Faster purchase handoff — 7 November 2026
The stock alert now puts the available Apple Store directly in the email subject, marks its priority high, includes a Sydney-local detection timestamp, and presents a clickable official Apple product-page link in both HTML and plain text email. It does not claim to reserve inventory or offer a preselected checkout session. Regression tests cover alert format and rejection of unavailable status.

See [FAST_CHECKOUT.md](FAST_CHECKOUT.md) for preparing Apple Account sign-in, balance and pickup details on your own iPhone before the next short-lived stock release. No account credentials are stored in the repository.

## Fast checkout handoff (7 November 2026)
Alerts now put `STOCK NOW` and the detected store name in the subject, and include the Sydney timestamp, exact SKU, and a one-tap link to the Apple Australia product page in HTML and plain text. The link opens the product page, **not** a guaranteed reserved cart or store-selected checkout. Final store selection, pickup window, Apple Account balance application, authentication, and purchase remain manual. Never store Apple Account credentials/cookies in GitHub. Email high-priority headers do not guarantee mobile push timing.

For best manual checkout speed, sign into Apple's store on a trusted iPhone beforehand, verify the purchase configuration and payment options, then use the alert link. Do not assume an item in the shopping bag is reserved. Regression tests cover available-only alert content without sending real email.

This change does not make GitHub's five-minute scheduled runner more frequent or guarantee that a stock window will remain open after an alert.

## Two-minute polling mode (7 November 2026)
GitHub Actions itself cannot reliably schedule new workflow runs every two minutes; instead, `stock-monitor.yml` launches approximately every **six minutes** using an explicit UTC `2-59/6 20-23,0-12 * * *` schedule (covering both AEST and AEDT) and `poll_stock.py` performs up to **three checks spaced 120 seconds apart** within each runner. The script enforces the **07:00 inclusive to 22:00 exclusive Australia/Sydney** window for each individual check, including manual dispatch and delayed runners. GitHub's scheduling and network latency mean this is a best-effort cadence, not a guaranteed real-time two-minute SLA.

The existing `stock_monitor.main()` still verifies exact candidate part `MK2E4X/A` at the seven Greater Sydney stores, sends Gmail only for previously unalerted confirmed `available` responses, and uses `.stock_alert_state.json` to suppress duplicates. Three consecutive checks share state within one runner; the workflow commits it once at the end, even if a later check fails. GitHub's concurrency group prevents overlapping runners from changing the same alert state in parallel. Five Apple postcode requests per check yield up to 15 postcode queries every six minutes (about 150 requests per hour if all execute); watch for HTTP 429/541 and reduce frequency if Apple imposes restrictions.

The test suite includes a fake-clock test for check timing, cutoff, error recovery and Australian daylight saving. To check CI: GitHub Actions -> Offline unit tests. To test real endpoint separately: manually run the stock-monitor workflow and inspect the logs.

## Scheduled-trigger repair (7 November 2026)
Earlier schedule used a `timezone` key. GitHub's standard Actions schedule is UTC-based; the observed automatic run was outside Sydney daytime, and morning checks were only manually dispatched. The workflow now uses a UTC six-minute cron covering the summer/winter Sydney-hour union, while `poll_stock.py` rejects all checks outside 07:00–22:00 Sydney local time. GitHub may delay or drop scheduled starts; this change cannot guarantee two-minute checks during every window. Continue verifying the scheduled event type (not `workflow_dispatch`) in Actions runs.
