"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { LogOut, LayoutDashboard, PlusCircle, Car, ShieldCheck } from "lucide-react";

export default function RiderLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!user || user.role !== "RIDER")) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading || !user) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="flex min-h-screen flex-col bg-[hsl(var(--color-surface))] md:flex-row">
      <aside className="w-full border-b border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface-2))] p-4 md:w-64 md:border-b-0 md:border-r md:p-6 flex flex-col">
        <div className="mb-8 flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-blue-500 flex items-center justify-center font-bold text-white">G</div>
          <span className="text-xl font-bold tracking-tight">GripWise</span>
        </div>
        
        <nav className="flex-1 space-y-2">
          <Link href="/dashboard" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-[hsl(var(--color-text))] hover:bg-[hsl(var(--color-surface-3))]">
            <LayoutDashboard className="h-4 w-4" /> Dashboard
          </Link>
          <Link href="/vehicles/new" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-[hsl(var(--color-text))] hover:bg-[hsl(var(--color-surface-3))]">
            <Car className="h-4 w-4" /> Add Vehicle
          </Link>
          <Link href="/inspections/new" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-[hsl(var(--color-text))] hover:bg-[hsl(var(--color-surface-3))]">
            <PlusCircle className="h-4 w-4" /> New Inspection
          </Link>
          <Link href="/consent" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-[hsl(var(--color-text))] hover:bg-[hsl(var(--color-surface-3))]">
            <ShieldCheck className="h-4 w-4" /> Mechanic Access
          </Link>
        </nav>

        <div className="mt-8 border-t border-[hsl(var(--color-border))] pt-4">
          <div className="mb-4 px-3 text-sm">
            <p className="font-medium">{user.display_name}</p>
            <p className="text-xs text-[hsl(var(--color-text-muted))]">Rider Account</p>
          </div>
          <button onClick={() => { logout(); router.push("/login"); }} className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-red-400 hover:bg-red-500/10">
            <LogOut className="h-4 w-4" /> Sign Out
          </button>
        </div>
      </aside>
      
      <main className="flex-1 p-4 md:p-8">
        <div className="mx-auto max-w-4xl">
          {children}
        </div>
      </main>
    </div>
  );
}
