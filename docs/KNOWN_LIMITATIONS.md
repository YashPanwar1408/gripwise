# GripWise Known Limitations

## Inspection results

- The default `mock` provider returns simulated demonstration output and does not analyze the uploaded image.
- The computer-vision provider can be selected only when its dependencies are available. It is not calibrated as a safety instrument and its output is not a physical tread-depth measurement.
- The condition classifier and remaining-tyre-life prediction are not available. GripWise does not claim accident reduction or validated AI accuracy.
- A qualified mechanic should physically inspect suspected tyre damage.

## Storage and deployment

- Uploaded images use local disk storage. Production deployment needs managed object storage, backups, monitoring, and deployment-specific security review.
- Docker Compose is configured for local development. Its credentials are development defaults and must not be reused in production.
- The local application and demo database are not a production service.

## Browser-authenticated pages

- Rider and mechanic report pages fetch protected data with a token restored from browser storage. Their segments are opted out of Next.js instant-navigation validation while they show the authenticated loading state; this is a development insight setting, not a hydration warning or a change to access control.

## Mechanic Growth

- Learning modules provide general educational material; they are not professional certification, warranties, or manufacturer endorsements.
- Recognition reflects recorded GripWise activity and the documented in-app criteria. Profile completion does not independently verify a workshop.
- Follow-up records should contain only the minimum information needed and may be saved only after the customer has agreed.

## Optional Partner Programmes

- Proposal examples are disabled by default. They appear only when `ENABLE_PARTNER_PROGRAMMES=true` is set for the backend and `NEXT_PUBLIC_ENABLE_PARTNER_PROGRAMMES=true` is set for the frontend.
- Enabling the display does not create an offer or imply a confirmed manufacturer partnership, sponsorship, funding, or accreditation.
