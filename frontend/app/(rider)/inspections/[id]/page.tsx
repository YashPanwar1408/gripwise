import { Suspense } from "react";
import InspectionDetailClient from "./inspection-detail-client";

// The report requires a browser token and is fetched after authentication restores.
export const instant = false;

function InspectionLoading() {
  return (
    <div className="p-8 text-center" role="status" aria-live="polite">
      Loading inspection report...
    </div>
  );
}

export default function InspectionDetailPage() {
  return (
    <Suspense fallback={<InspectionLoading />}>
      <InspectionDetailClient />
    </Suspense>
  );
}
