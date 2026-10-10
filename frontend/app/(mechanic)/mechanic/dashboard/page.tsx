"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { mechanicApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Inspection } from "@/lib/types";
import { RefreshCw, Search, ShieldCheck } from "lucide-react";

export default function MechanicDashboard() {
  const { user } = useAuth();
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadInspections = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const res = await mechanicApi.getInspections(user.access_token);
      setInspections(res.inspections);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInspections();
  }, [user]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold mb-2">Service Queue</h1>
          <p className="text-[hsl(var(--color-text-muted))]">Inspections authorized for your workshop.</p>
        </div>
        <button onClick={loadInspections} className="btn-secondary flex items-center gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && <div className="p-4 bg-red-500/10 text-red-400 rounded-lg">{error}</div>}

      <div className="card">
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(var(--color-text-muted))]" />
          <input 
            type="text" 
            placeholder="Search by Inspection ID..." 
            className="input pl-10"
          />
        </div>

        {loading ? (
          <div className="py-12 text-center text-[hsl(var(--color-text-muted))]">Loading queue...</div>
        ) : inspections.length === 0 ? (
          <div className="py-12 text-center border-2 border-dashed border-[hsl(var(--color-border))] rounded-xl">
            <ShieldCheck className="h-12 w-12 text-green-500/50 mx-auto mb-4" />
            <h3 className="text-lg font-bold mb-2">Queue is Empty</h3>
            <p className="text-[hsl(var(--color-text-muted))] max-w-md mx-auto">
              No riders have authorized your workshop to view their inspections recently. 
              Ask riders to generate a consent code from their GripWise app.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {inspections.map(insp => (
              <Link 
                href={`/mechanic/inspections/${insp.inspection_id}`} 
                key={insp.inspection_id}
                className="flex items-center justify-between p-4 rounded-xl border border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface-2))] hover:border-orange-500/50 transition-colors group"
              >
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-mono text-sm text-[hsl(var(--color-text))]">{insp.inspection_id.split('-')[0]}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${insp.status === 'COMPLETE' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'}`}>
                      {insp.status}
                    </span>
                  </div>
                  <div className="text-sm text-[hsl(var(--color-text-muted))]">
                    {new Date(insp.created_at).toLocaleString()}
                  </div>
                </div>
                
                {insp.recommended_action && (
                  <div className="text-right">
                    <div className="text-xs text-[hsl(var(--color-text-muted))] uppercase tracking-wider mb-1">AI Recommendation</div>
                    <div className="font-bold text-[hsl(var(--color-text))] capitalize">{insp.recommended_action.replace(/_/g, ' ')}</div>
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
