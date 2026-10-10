"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { mechanicApi, inspectionsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Inspection } from "@/lib/types";
import { ObservationCard, SafetyDisclaimer } from "@/components/inspection/ObservationCard";
import { ArrowLeft, Save, ShieldCheck, CheckCircle2 } from "lucide-react";

export default function MechanicInspectionDetail() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const { user } = useAuth();
  
  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user) {
      // Mechanics can read the inspection if they have consent
      mechanicApi.getInspection(user.access_token, id)
        .then(setInspection)
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [user, id]);

  const handleSubmitFinding = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!user) return;
    
    setSaving(true);
    const form = new FormData(e.currentTarget);
    const body = {
      tread_depth_mm: form.get("tread_depth") ? parseFloat(form.get("tread_depth") as string) : undefined,
      pressure_psi: form.get("pressure") ? parseFloat(form.get("pressure") as string) : undefined,
      notes: form.get("notes") as string
    };
    
    try {
      await mechanicApi.addFinding(user.access_token, id, body);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
      e.currentTarget.reset();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!inspection) return <div className="text-red-400">Not authorized or not found.</div>;

  return (
    <div className="space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-sm text-[hsl(var(--color-text-muted))] hover:text-white transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Queue
      </button>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Inspection Review</h1>
          <p className="text-sm text-[hsl(var(--color-text-muted))]">ID: {inspection.inspection_id}</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Left Column: AI Data */}
        <div className="space-y-6">
          <div className="flex items-center gap-2 mb-4 text-[hsl(var(--color-text-muted))]">
            <ShieldCheck className="h-5 w-5" />
            <h2 className="font-semibold text-lg text-white">AI Observations</h2>
          </div>
          
          <SafetyDisclaimer />

          <div className="grid gap-4">
            {inspection.observations.map((obs, i) => (
              <ObservationCard key={i} obs={obs} />
            ))}
          </div>
        </div>

        {/* Right Column: Mechanic Input */}
        <div className="space-y-6">
          <div className="flex items-center gap-2 mb-4 text-orange-400">
            <CheckCircle2 className="h-5 w-5" />
            <h2 className="font-semibold text-lg text-white">Mechanic Verification</h2>
          </div>

          <div className="card border-orange-500/20 bg-orange-500/5">
            <p className="text-sm text-[hsl(var(--color-text-muted))] mb-6">
              Record your physical findings here. This adds a "Verified" badge to the rider's report.
            </p>

            <form onSubmit={handleSubmitFinding} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Actual Tread (mm)</label>
                  <input name="tread_depth" type="number" step="0.1" className="input" placeholder="e.g. 1.8" />
                </div>
                <div>
                  <label className="label">Pressure (PSI)</label>
                  <input name="pressure" type="number" className="input" placeholder="e.g. 28" />
                </div>
              </div>
              
              <div>
                <label className="label">Mechanic Notes</label>
                <textarea name="notes" className="input min-h-[100px]" placeholder="Add professional recommendations..." required></textarea>
              </div>

              <button type="submit" disabled={saving} className="btn-primary w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600">
                {saving ? "Saving..." : (
                  <>
                    <Save className="h-4 w-4" /> Save Findings
                  </>
                )}
              </button>
              
              {saved && <p className="text-green-400 text-sm text-center">Findings saved successfully!</p>}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
