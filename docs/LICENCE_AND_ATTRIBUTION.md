# Licence and Attribution

GripWise was developed for the Tata Imagination Challenge and Eurogrip TORQ Challenge 4.0. It incorporates carefully audited components from the provided reference repositories.

## 1. tyreHealth
- **Original Source**: `refrences/tyreHealth-main/`
- **Purpose**: Computer Vision (CV) pipelines for tread anomaly detection.
- **Integration Details**: The algorithms for circularity mapping and tread proxy scoring were adapted from `cv_pipeline.py` and wrapped behind GripWise's `InferenceProvider` interface to ensure type safety and fail-over capability. 
- **Modifications**: Raw percentage metrics were replaced with qualitative confidence tiers. Hardcoded file paths and dangerous subprocess calls were stripped out.
- **Licence Compliance**: Adheres to the MIT License provided in the reference repository. We do not claim original ownership of the core CV algorithms.

## 2. BharatDrive-x-Twin
- **Original Source**: `refrences/BharatDrive-x-Twin-main/`
- **Purpose**: Architectural inspiration.
- **Integration Details**: Did not merge source code directly due to severe architectural disparities and unverified data claims. Inspired the conceptual design of the dual Rider/Mechanic persona workflows.
- **Modifications**: N/A (No raw code executed).

## Third-Party Open Source Software
GripWise utilizes the following open-source frameworks:
- **FastAPI**: (MIT License) - High-performance backend API framework.
- **SQLAlchemy**: (MIT License) - ORM and database toolkit.
- **Next.js / React**: (MIT License) - Frontend rendering framework.
- **OpenCV**: (Apache 2.0) - Image processing libraries (used in the CV provider).

**Notice**: GripWise does not claim any official partnership with Eurogrip or Tata Motors. The platform is a conceptual prototype developed exclusively for the hackathon context.
