"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { vehiclesApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function NewVehicle() {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!user) return;
    setLoading(true);
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      // Step 1: Create Vehicle
      const vehicle = await vehiclesApi.create(user.access_token, {
        make: form.get("make") as string,
        model: form.get("model") as string,
        year: form.get("year") ? parseInt(form.get("year") as string) : undefined,
        registration: form.get("registration") as string,
        vehicle_type: form.get("vehicle_type") as string,
      });

      // Step 2: Auto-create front and rear tyre positions for MOTORCYCLE / SCOOTER
      if (vehicle.vehicle_type === "MOTORCYCLE" || vehicle.vehicle_type === "SCOOTER") {
        await Promise.all([
          vehiclesApi.addTyrePosition(user.access_token, vehicle.vehicle_id, { position: "FRONT" }),
          vehiclesApi.addTyrePosition(user.access_token, vehicle.vehicle_id, { position: "REAR" }),
        ]);
      }

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Register New Vehicle</h1>
        <p className="text-[hsl(var(--color-text-muted))]">Add your two-wheeler to start tracking tyre health.</p>
      </div>

      {error && <div className="mb-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-400">{error}</div>}

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Make / Brand</label>
            <input name="make" type="text" required className="input" placeholder="e.g. Royal Enfield" />
          </div>
          <div>
            <label className="label">Model</label>
            <input name="model" type="text" required className="input" placeholder="e.g. Classic 350" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Vehicle Type</label>
            <select name="vehicle_type" required className="input">
              <option value="MOTORCYCLE">Motorcycle</option>
              <option value="SCOOTER">Scooter</option>
              <option value="BICYCLE">Bicycle</option>
            </select>
          </div>
          <div>
            <label className="label">Year (Optional)</label>
            <input name="year" type="number" min="1990" max={new Date().getFullYear()} className="input" placeholder="2023" />
          </div>
        </div>

        <div>
          <label className="label">Registration Number (Optional)</label>
          <input name="registration" type="text" className="input" placeholder="MH 12 AB 1234" />
        </div>

        <div className="pt-4 flex gap-3">
          <button type="button" onClick={() => router.back()} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={loading} className="btn-primary flex-1">
            {loading ? "Saving..." : "Save Vehicle"}
          </button>
        </div>
      </form>
    </div>
  );
}
