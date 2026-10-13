"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { vehiclesApi, inspectionsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDate } from "@/lib/format-date";
import type { Vehicle, Inspection } from "@/lib/types";
import { Car, Camera, Clock, AlertTriangle, AlertCircle } from "lucide-react";

export default function Dashboard() {
  const { user } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    Promise.all([
      vehiclesApi.list(user.access_token),
      inspectionsApi.list(user.access_token)
    ]).then(([vRes, iRes]) => {
      setVehicles(vRes.vehicles);
      setInspections(iRes.inspections);
      setLoading(false);
    }).catch(console.error);
  }, [user]);

  if (loading) return <div>Loading dashboard...</div>;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold">Welcome back, {user?.display_name?.split(" ")[0]}</h1>
        <p className="text-[hsl(var(--color-text-muted))]">Here's your tyre safety overview.</p>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2"><Car className="h-5 w-5 text-blue-400" /> My Vehicles</h2>
            <Link href="/vehicles/new" className="text-sm font-medium text-blue-400 hover:underline">Add</Link>
          </div>
          {vehicles.length === 0 ? (
            <p className="text-sm text-[hsl(var(--color-text-muted))]">No vehicles added yet.</p>
          ) : (
            <div className="space-y-3">
              {vehicles.map((v) => (
                <div key={v.vehicle_id} className="rounded-xl border border-[hsl(var(--color-border))] p-3 flex justify-between items-center bg-[hsl(var(--color-surface-3))]">
                  <div>
                    <p className="font-medium">{v.make} {v.model}</p>
                    <p className="text-xs text-[hsl(var(--color-text-muted))]">{v.registration} • {v.tyre_positions.length} tyres logged</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2"><Clock className="h-5 w-5 text-orange-400" /> Recent Inspections</h2>
            <Link href="/inspections/new" className="text-sm font-medium text-blue-400 hover:underline">New</Link>
          </div>
          {inspections.length === 0 ? (
            <p className="text-sm text-[hsl(var(--color-text-muted))]">No inspections yet.</p>
          ) : (
            <div className="space-y-3">
              {inspections.slice(0, 5).map((insp) => (
                <Link key={insp.inspection_id} href={`/inspections/${insp.inspection_id}`} className="block rounded-xl border border-[hsl(var(--color-border))] p-3 hover:border-blue-500/50 bg-[hsl(var(--color-surface-3))] transition-colors">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium">Inspection #{insp.inspection_id.slice(0, 6)}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                      insp.status === 'COMPLETE' ? 'bg-green-500/10 text-green-400' :
                      insp.status === 'FAILED' ? 'bg-red-500/10 text-red-400' : 'bg-blue-500/10 text-blue-400'
                    }`}>{insp.status}</span>
                  </div>
                  <div className="flex justify-between items-end text-xs text-[hsl(var(--color-text-muted))]">
                    <span>{formatDate(insp.created_at)}</span>
                    {insp.recommended_action && <span className="text-[hsl(var(--color-text))] font-medium capitalize flex items-center gap-1"><AlertCircle className="h-3 w-3" /> {insp.recommended_action.replace(/_/g, ' ')}</span>}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
