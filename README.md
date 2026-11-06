# Sydney iPhone Duo stock checker

**Status: validation only; no scheduled checks or stock alerts enabled.**

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
