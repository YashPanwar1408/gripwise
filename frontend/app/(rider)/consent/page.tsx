"use client";
import { useEffect, useState } from "react";
import { consentApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDate } from "@/lib/format-date";
import type { ConsentRecord } from "@/lib/types";
import { ShieldAlert, ShieldCheck, Trash2, Key } from "lucide-react";

export default function ConsentManagement() {
  const { user } = useAuth();
  const [consents, setConsents] = useState<ConsentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [granting, setGranting] = useState(false);
  const [error, setError] = useState("");

  const fetchConsents = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const res = await consentApi.list(user.access_token);
      setConsents(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConsents();
  }, [user]);

  const handleGrant = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!user) return;
    const form = e.currentTarget;
    const mechanicId = String(new FormData(form).get("mechanic_id") ?? "").trim();
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(mechanicId)) {
      setError("Enter the mechanic's full Workshop ID. It is a UUID shown on their Service Queue page.");
      return;
    }

    setGranting(true);
    setError("");
    try {
      await consentApi.grant(user.access_token, mechanicId);
      form.reset();
      await fetchConsents();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setGranting(false);
    }
  };

  const handleRevoke = async (id: string) => {
    if (!user) return;
    if (!confirm("Revoke mechanic access? They will immediately lose access to your inspection data.")) return;
    
    try {
      await consentApi.revoke(user.access_token, id);
      fetchConsents();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2 flex items-center gap-3">
          <ShieldCheck className="h-6 w-6 text-green-500" /> Mechanic Access
        </h1>
        <p className="text-[hsl(var(--color-text-muted))]">
          Control which mechanics can view your AI inspection reports and log service records. You are in total control of your data.
        </p>
      </div>

      {error && <div className="p-4 bg-red-500/10 text-red-400 rounded-lg">{error}</div>}

      <div className="card">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><Key className="h-5 w-5" /> Grant Access</h2>
        <form onSubmit={handleGrant} className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="label">Mechanic ID</label>
            <input
              name="mechanic_id"
              type="text"
              className="input"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              autoComplete="off"
              minLength={36}
              maxLength={36}
              pattern="[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
              title="Enter the mechanic's full 36-character Workshop ID."
              required
            />
            <p className="mt-2 text-xs text-[hsl(var(--color-text-muted))]">
              Ask the mechanic to copy their Workshop ID from the Service Queue page. Enter the full UUID, not a phone number or short numeric code.
            </p>
          </div>
          <button type="submit" disabled={granting} className="btn-primary">
            {granting ? "Granting..." : "Grant Access"}
          </button>
        </form>
      </div>

      <div className="card">
        <h2 className="text-lg font-bold mb-4">Active Authorizations</h2>
        
        {loading ? (
          <div className="py-8 text-center text-[hsl(var(--color-text-muted))]">Loading active consents...</div>
        ) : consents.length === 0 ? (
          <div className="py-12 text-center border-2 border-dashed border-[hsl(var(--color-border))] rounded-xl">
            <ShieldAlert className="h-12 w-12 text-[hsl(var(--color-text-muted))] mx-auto mb-4" />
            <h3 className="font-semibold mb-2">No active access</h3>
            <p className="text-sm text-[hsl(var(--color-text-muted))]">Your data is completely private. No mechanics have access to your inspections.</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-lg border border-[hsl(var(--color-border))]">
            <table className="w-full text-left text-sm">
              <thead className="bg-[hsl(var(--color-surface-2))]">
                <tr>
                  <th className="p-4 font-medium text-[hsl(var(--color-text-muted))]">Mechanic ID</th>
                  <th className="p-4 font-medium text-[hsl(var(--color-text-muted))]">Granted On</th>
                  <th className="p-4 font-medium text-[hsl(var(--color-text-muted))] text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[hsl(var(--color-border))]">
                {consents.map(consent => (
                  <tr key={consent.id} className="hover:bg-[hsl(var(--color-surface-3))] transition-colors">
                    <td className="p-4 font-mono">{consent.mechanic_id}</td>
                    <td className="p-4">{formatDate(consent.granted_at)}</td>
                    <td className="p-4 text-right">
                      <button 
                        onClick={() => handleRevoke(consent.id)}
                        className="text-red-400 hover:text-red-300 p-2 hover:bg-red-500/10 rounded transition-colors"
                        title="Revoke Access"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
