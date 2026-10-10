"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function Login() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      const res = await authApi.login(form.get("credential") as string, form.get("password") as string);
      setUser(res);
      if (res.role === "MECHANIC") {
        router.push("/mechanic/dashboard");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-md card">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold">Sign In to GripWise</h1>
          <p className="text-[hsl(var(--color-text-muted))]">Manage your tyre safety</p>
        </div>
        
        {error && <div className="mb-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-400">{error}</div>}

        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <div>
            <label className="label">Email or Mobile</label>
            <input name="credential" type="text" required className="input" placeholder="rider@test.com" />
          </div>
          <div>
            <label className="label">Password</label>
            <input name="password" type="password" required className="input" placeholder="••••••••" />
          </div>
          <button type="submit" disabled={loading} className="btn-primary mt-2">
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-[hsl(var(--color-text-muted))]">
          Don't have an account? <Link href="/register" className="text-blue-400 hover:underline">Register</Link>
        </p>
      </div>
    </div>
  );
}
