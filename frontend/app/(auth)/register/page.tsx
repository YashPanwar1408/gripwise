"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function Register() {
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
      const res = await authApi.register({
        display_name: form.get("display_name") as string,
        email: form.get("email") as string,
        password: form.get("password") as string,
        role: "RIDER",
      });
      setUser(res);
      router.push("/dashboard");
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
          <h1 className="text-2xl font-bold">Create Account</h1>
          <p className="text-[hsl(var(--color-text-muted))]">Join GripWise as a Rider</p>
        </div>
        
        {error && <div className="mb-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-400">{error}</div>}

        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <div>
            <label className="label">Full Name</label>
            <input name="display_name" type="text" required className="input" placeholder="Rahul Sharma" />
          </div>
          <div>
            <label className="label">Email</label>
            <input name="email" type="email" required className="input" placeholder="rahul@example.com" />
          </div>
          <div>
            <label className="label">Password (min 8 chars)</label>
            <input name="password" type="password" required minLength={8} className="input" placeholder="••••••••" />
          </div>
          <button type="submit" disabled={loading} className="btn-primary mt-2">
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-[hsl(var(--color-text-muted))]">
          Already have an account? <Link href="/login" className="text-blue-400 hover:underline">Sign In</Link>
        </p>
      </div>
    </div>
  );
}
