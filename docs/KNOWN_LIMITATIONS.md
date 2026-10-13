# GripWise Known Limitations

While GripWise is fundamentally robust and hackathon-ready, the following limitations are explicitly acknowledged to ensure full transparency during judging:

## 1. Deep Learning / CNN Classifier Omission
- **Description**: The advanced CNN condition classifier (`classifier_model.h5` / `model.pt`) from the `tyreHealth` reference repository was **omitted**.
- **Reason**: The pre-trained model weights were absent from the repository, and the training data provenance was unverified. GripWise adheres to strict policies against deploying unverified "black-box" models or making unsupported safety claims.
- **Impact**: Classification of specific edge cases (e.g., sidewall bulging) relies on manual mechanic verification rather than automated AI categorization. The backend gracefully reports `condition_classifier_available=false`.

## 2. Telemetry and Lifespan Prediction
- **Description**: The "lifespan prediction" algorithm from `BharatDrive-x-Twin` was not integrated.
- **Reason**: Predicting tyre lifespan requires real-time telemetry, IoT integration, and historical datasets which are entirely simulated in a hackathon environment. Fabricating this data violates our product vision of trust and transparency.
- **Impact**: We provide a deterministic "Tread Wear Proxy Score" instead of a fabricated "Miles Remaining" metric.

## 3. Storage and Scaling
- **Description**: Images are currently saved to the local disk (`/uploads`).
- **Reason**: Cloud storage (AWS S3 / GCP Cloud Storage) integration was deferred to prioritize core workflow logic and prevent configuration overhead during the hackathon.
- **Impact**: The application is stateful. Moving to production requires abstracting the file system layer to an S3-compatible blob store.

## 4. UI Polish and Transitions
- **Description**: While the mechanic and consent workflows are fully functional, some edge-case transitions or advanced loading states might be minimal.
- **Reason**: The focus was primarily on ensuring the API and database role-based access controls were flawless, followed by a functional and beautiful UI.
- **Impact**: Demonstrating edge cases (like network failure during upload) relies on basic alerts.

## 5. Mock AI Provider
- **Description**: The `MOCK` AI provider is configured as the default for demonstration purposes.
- **Reason**: Hardware constraints on presentation machines may prevent running OpenCV/YOLO inference in real-time.
- **Impact**: When in mock mode, the system returns deterministic, safe fallback data. The real `CVProvider` can be activated by changing `INFERENCE_PROVIDER=cv` in `.env`, provided OpenCV and YOLO dependencies are available in the host environment.

## 6. Eurogrip TORQ Challenge 4.0 Programme Scope
- **Description**: The proposed tool-support initiatives (digital tread depth gauges, calibrated pressure stations, and brand masterclasses) are conceptual strategic proposals designed specifically for Case Study 4.
- **Reason**: GripWise is a technology prototype and competition solution, not a corporate subsidiary of TVS Srichakra / Eurogrip.
- **Impact**: The application deliberately makes no claims of existing commercial funding, inventory warehousing, dealer trade discounts, or official corporate sponsorships.

## 7. Educational Content Scope & Privacy
- **Description**: The Tyre-Care Learning Hub curriculum is grounded in open engineering standards (ISO 4223, ETRTO, BS AU 159, RMA guidelines) rather than proprietary manufacturer proprietary certifications.
- **Reason**: Mechanics operate across diverse two-wheeler brands. General tyre engineering principles protect rider safety without brand bias.
- **Impact**: Customer follow-up records use masked references (e.g. "Ramesh K.", "+91 98*** **321") to uphold strict personal data minimization and avoid storing unneeded customer PII.
