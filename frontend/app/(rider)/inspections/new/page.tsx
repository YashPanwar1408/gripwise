"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { vehiclesApi, inspectionsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Vehicle } from "@/lib/types";
import { Camera, UploadCloud, RefreshCw } from "lucide-react";

export default function NewInspection() {
  const router = useRouter();
  const { user } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selectedTyreId, setSelectedTyreId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (user) {
      vehiclesApi.list(user.access_token)
        .then(res => {
          setVehicles(res.vehicles);
          const firstTyre = res.vehicles[0]?.tyre_positions[0];
          if (firstTyre) setSelectedTyreId(firstTyre.tyre_position_id);
        })
        .catch(console.error);
    }
  }, [user]);

  const handleFile = (f: File | null) => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(f);
    setPreviewUrl(f ? URL.createObjectURL(f) : null);
  };

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!user || !selectedTyreId || !file) return;
    setLoading(true);
    setError("");
    try {
      const res = await inspectionsApi.submit(user.access_token, selectedTyreId, file);
      // Wait a moment for background processing to start, then redirect to inspection detail
      setTimeout(() => {
        router.push(`/inspections/${res.inspection_id}`);
      }, 1000);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="card max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">New AI Inspection</h1>
        <p className="text-[hsl(var(--color-text-muted))]">Upload a clear photo of your tyre tread.</p>
      </div>

      <div className="demo-banner mb-6">
        <strong>Demo Mode:</strong> The AI provider is mocked. Image quality checks and observations are deterministically generated based on image contents.
      </div>

      {error && <div className="mb-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-400">{error}</div>}

      <form onSubmit={onSubmit} className="space-y-6">
        <div>
          <label className="label">Select Tyre</label>
          <select value={selectedTyreId} onChange={e => setSelectedTyreId(e.target.value)} required className="input">
            <option value="" disabled>Select a vehicle and tyre</option>
            {vehicles.map(v => (
              <optgroup key={v.vehicle_id} label={`${v.make} ${v.model}`}>
                {v.tyre_positions.map(tp => (
                  <option key={tp.tyre_position_id} value={tp.tyre_position_id}>
                    {tp.position} TYRE
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div>
          <label className="label mb-2">Tyre Photo</label>
          <input 
            type="file" accept="image/jpeg,image/png,image/webp" required
            ref={fileInputRef} className="hidden"
            onChange={e => handleFile(e.target.files?.[0] || null)}
          />
          
          <div 
            onClick={() => fileInputRef.current?.click()}
            className={`cursor-pointer overflow-hidden rounded-xl border-2 border-dashed transition-all ${
              previewUrl ? 'border-blue-500/50 bg-[hsl(var(--color-surface-3))]' : 'border-[hsl(var(--color-border))] hover:border-blue-500/30 bg-[hsl(var(--color-surface-3))]'
            }`}
          >
            {previewUrl ? (
              <div className="relative aspect-video w-full">
                <img src={previewUrl} alt="Preview" className="h-full w-full object-cover" />
                <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition-opacity hover:opacity-100">
                  <p className="flex items-center gap-2 font-medium text-white"><Camera className="h-5 w-5" /> Change Photo</p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-[hsl(var(--color-text-muted))]">
                <UploadCloud className="mb-3 h-10 w-10 opacity-70" />
                <p className="font-medium text-[hsl(var(--color-text))]">Click to upload image</p>
                <p className="mt-1 text-xs">JPEG, PNG or WebP (max 10MB)</p>
              </div>
            )}
          </div>
        </div>

        <div className="pt-2">
          <button type="submit" disabled={loading || !file || !selectedTyreId} className="btn-primary w-full py-4 text-base">
            {loading ? (
              <span className="flex items-center gap-2"><RefreshCw className="h-5 w-5 animate-spin" /> Analyzing Tyre...</span>
            ) : (
              <span className="flex items-center gap-2"><Camera className="h-5 w-5" /> Analyze Tyre</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
