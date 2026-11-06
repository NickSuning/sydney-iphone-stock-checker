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
