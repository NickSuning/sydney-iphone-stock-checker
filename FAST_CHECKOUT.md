# Fast Apple checkout checklist

**Target only:** iPhone Duo, 256GB, Night Sky (candidate Australian SKU `MK2E4X/A`). Do not accept a substitute configuration.

The checker sends a high-priority email with the Sydney store name, timestamp and a clickable link to Apple's exact product page. It does **not** reserve stock or automatically select a store, pickup time, payment method, or place an order.

## Prepare once on your own iPhone
1. Sign into the correct Apple Account in the Apple Store app or Safari and make sure sign-in/two-factor authentication works.
2. Review that the Apple Account balance is sufficient and available for the intended hardware purchase. Apple determines actual eligibility during checkout.
3. Check your saved contact details, pickup identity and billing information in Apple checkout. Do not save Apple credentials or session cookies in GitHub.
4. Enable immediate push notifications for your 126.com mailbox; optionally configure a distinctive sound for messages with `STOCK NOW` in the subject.
5. Open the Apple product page beforehand and verify the exact colour/capacity and any saved bag or favourites options. Saved shopping bags are **not** stock reservations.

## When an alert arrives
1. Tap the official Apple product-page link in the email immediately.
2. Reconfirm **256GB Night Sky** and choose the **named Apple Store**.
3. Pick the earliest pickup option actually offered by Apple. No time slot is guaranteed by the inventory API.
4. Apply Apple Account balance if Apple offers it at checkout; confirm any remaining amount.
5. Submit the order personally and wait for Apple's confirmation. Only Apple's accepted order confirms the purchase; an alert or shopping bag does not.

## What the notification means
- The checked Apple Australia pickup response contained `pickupDisplay=available` for the exact SKU at the named store.
- Stock may disappear before checkout. GitHub Actions scheduling and email push delivery are not instantaneous.
- The email's purchase-page link opens the exact product listing; it is not an authenticated, store-specific reserved checkout session.
