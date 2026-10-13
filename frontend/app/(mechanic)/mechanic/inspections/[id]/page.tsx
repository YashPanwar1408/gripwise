import { Suspense } from "react";
import MechanicInspectionDetailClient from "./mechanic-inspection-detail-client";

// Inspection access depends on rider consent and a browser-restored mechanic token.
export const instant = false;

function InspectionLoading() {
  return (
    <div className="p-8 text-center" role="status" aria-live="polite">
      Loading inspection report...
    </div>
  );
}

export default function MechanicInspectionDetailPage() {
  return (
    <Suspense fallback={<InspectionLoading />}>
      <MechanicInspectionDetailClient />
    </Suspense>
  );
}
