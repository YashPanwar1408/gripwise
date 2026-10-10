import React from "react";
import type { ConfidenceTier, InspectionObservation } from "@/lib/types";
import { AlertTriangle, CheckCircle2, HelpCircle, ShieldAlert } from "lucide-react";

export function ConfidenceBadge({ tier }: { tier: ConfidenceTier }) {
  const config = {
    HIGH_CONFIDENCE: { label: "High Confidence", color: "text-green-400 bg-green-500/10 border-green-500/20" },
    MEDIUM_CONFIDENCE: { label: "Medium Confidence", color: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20" },
    LOW_CONFIDENCE: { label: "Low Confidence", color: "text-orange-400 bg-orange-500/10 border-orange-500/20" },
    NOT_AVAILABLE: { label: "Not Available", color: "text-slate-400 bg-slate-500/10 border-slate-500/20" },
  };
  const c = config[tier] || config.NOT_AVAILABLE;

  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${c.color}`}>
      {c.label}
    </span>
  );
}

export function ObservationCard({ obs }: { obs: InspectionObservation }) {
  const formatValue = (v: any) => {
    if (v === null) return "N/A";
    if (typeof v === "boolean") return v ? "Yes" : "No";
    if (typeof v === "number") return v.toFixed(1);
    return v;
  };

  return (
    <div className="card-sm flex flex-col gap-3">
      <div className="flex items-start justify-between">
        <h4 className="text-sm font-semibold capitalize text-[hsl(var(--color-text))]">
          {obs.field.replace(/_/g, " ")}
        </h4>
        <ConfidenceBadge tier={obs.confidence} />
      </div>
      <div className="text-2xl font-bold">
        {formatValue(obs.value)}
      </div>
      <p className="text-xs text-[hsl(var(--color-text-muted))]">
        {obs.explanation}
      </p>
      {obs.caveat && (
        <div className="mt-2 flex gap-2 rounded-lg bg-orange-500/5 p-2 text-xs text-orange-200/80">
          <AlertTriangle className="h-4 w-4 shrink-0 text-orange-400" />
          <p>{obs.caveat}</p>
        </div>
      )}
    </div>
  );
}

export function SafetyDisclaimer() {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4 text-sm text-blue-200">
      <ShieldAlert className="h-5 w-5 shrink-0 text-blue-400 mt-0.5" />
      <div>
        <p className="font-semibold mb-1 text-blue-300">Safety Disclaimer</p>
        <p className="opacity-90">
          This system provides AI-assisted observations to help you monitor your tyre condition.
          It does <strong>not</strong> guarantee road safety and cannot replace a physical inspection
          by a qualified mechanic. Always consult a professional if you suspect tyre damage.
        </p>
      </div>
    </div>
  );
}
