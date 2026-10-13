"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { inspectionsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Inspection } from "@/lib/types";
import { ObservationCard, SafetyDisclaimer } from "@/components/inspection/ObservationCard";
import { RefreshCw, ArrowLeft, Image as ImageIcon, AlertTriangle, CheckCircle2 } from "lucide-react";

export default function InspectionDetail() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const { user } = useAuth();
  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchInspection = async () => {
    if (!user) return;
    try {
      const res = await inspectionsApi.get(user.access_token, id);
      setInspection(res);
      if (res.status === "PENDING" || res.status === "PROCESSING") {
        setTimeout(fetchInspection, 2000);
      } else {
        setLoading(false);
      }
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspection();
  }, [user, id]);

  if (loading && !inspection) return <div className="p-8 text-center flex justify-center items-center gap-3"><RefreshCw className="h-5 w-5 animate-spin" /> Loading inspection...</div>;
  if (error) return <div className="p-8 text-center text-red-400">Error: {error}</div>;
  if (!inspection) return null;

  const isComplete = inspection.status === "COMPLETE";
  const isProcessing = inspection.status === "PENDING" || inspection.status === "PROCESSING";

  const getActionColor = (action: string | null) => {
    if (action === "ok") return "text-green-400 bg-green-500/10 border-green-500/20";
    if (action === "monitor") return "text-yellow-400 bg-yellow-500/10 border-yellow-500/20";
    if (action === "inspect_soon") return "text-orange-400 bg-orange-500/10 border-orange-500/20";
    return "text-red-400 bg-red-500/10 border-red-500/20";
  };

  return (
    <div className="space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-sm text-[hsl(var(--color-text-muted))] hover:text-white transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back
      </button>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            Inspection Report
            {isProcessing && <RefreshCw className="h-5 w-5 animate-spin text-blue-400" />}
          </h1>
          <p className="text-sm text-[hsl(var(--color-text-muted))]">ID: {inspection.inspection_id}</p>
        </div>
        <div className="flex gap-2">
          {inspection.mechanic_verified && (
            <div className="px-3 py-1 rounded-full text-xs font-bold uppercase border bg-orange-500/10 text-orange-400 border-orange-500/20 flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3" /> Mechanic Verified
            </div>
          )}
          <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase border ${
            isComplete ? "bg-green-500/10 text-green-400 border-green-500/20" :
            inspection.status === "FAILED" ? "bg-red-500/10 text-red-400 border-red-500/20" :
            "bg-blue-500/10 text-blue-400 border-blue-500/20"
          }`}>
            {inspection.status}
          </div>
        </div>
      </div>

      <SafetyDisclaimer />

      {isProcessing && (
        <div className="card text-center py-12">
          <RefreshCw className="h-10 w-10 animate-spin mx-auto text-blue-500 mb-4" />
          <h3 className="text-lg font-semibold">Analyzing Image...</h3>
          <p className="text-[hsl(var(--color-text-muted))]">Our AI is currently inspecting your tyre.</p>
        </div>
      )}

      {isComplete && (
        <>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="md:col-span-1 space-y-6">
              <div className="card">
                <h3 className="font-semibold mb-4 border-b border-[hsl(var(--color-border))] pb-2">Analysis Metadata</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-[hsl(var(--color-text-muted))]">Image Quality</span>
                    <span className={`font-medium ${inspection.image_quality.status === 'PASS' ? 'text-green-400' : 'text-orange-400'}`}>
                      {inspection.image_quality.status}
                    </span>
                  </div>
                  {inspection.image_quality.issues.length > 0 && (
                    <div className="text-xs text-orange-400 bg-orange-500/10 p-2 rounded mt-1">
                      Issues: {inspection.image_quality.issues.join(", ")}
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-[hsl(var(--color-text-muted))]">AI Provider</span>
                    <span className="font-medium text-[hsl(var(--color-text))]">{inspection.inference_provider}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[hsl(var(--color-text-muted))]">Model Time</span>
                    <span className="font-medium text-[hsl(var(--color-text))]">{inspection.inference_ms?.toFixed(0)} ms</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="md:col-span-2 space-y-6">
              <div className={`rounded-xl border p-6 bg-[hsl(var(--color-surface-2))] ${getActionColor(inspection.recommended_action).replace('bg-', 'bg-opacity-10 bg-').split(' ')[2]}`}>
                <h2 className="text-xs font-bold uppercase tracking-wider text-[hsl(var(--color-text-muted))] mb-1">Recommended Action</h2>
                <div className={`text-2xl font-bold capitalize mb-2 ${getActionColor(inspection.recommended_action).split(' ')[0]}`}>
                  {inspection.recommended_action?.replace(/_/g, ' ')}
                </div>
                <p className="text-[hsl(var(--color-text))]">{inspection.recommended_action_explanation}</p>
              </div>

              <div>
                <h3 className="font-semibold mb-4 text-lg">AI Observations</h3>
                <div className="grid sm:grid-cols-2 gap-4">
                  {inspection.observations.map((obs, i) => (
                    <ObservationCard key={i} obs={obs} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {inspection.status === "FAILED" && (
        <div className="card border-red-500/30 bg-red-500/5">
          <div className="flex items-center gap-3 text-red-400 mb-2">
            <AlertTriangle className="h-6 w-6" />
            <h3 className="text-lg font-bold">Analysis Failed</h3>
          </div>
          <p className="text-red-200">The AI provider failed to process this image. Please try again with a clearer photo.</p>
        </div>
      )}
    </div>
  );
}
