"use client";
import { Suspense, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { LogOut, Wrench, Award, ClipboardList } from "lucide-react";

function MechanicNavLinks() {
  const pathname = usePathname();
  const isGrowth = pathname?.startsWith("/mechanic/saathi");
  const isQueue = pathname?.startsWith("/mechanic/dashboard") || pathname?.startsWith("/mechanic/inspections");

  return (
    <>
      <nav className="hidden md:flex items-center gap-2">
        <Link
          href="/mechanic/dashboard"
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium transition-all ${
            isQueue
              ? "bg-[hsl(var(--color-surface-3))] text-white border border-[hsl(var(--color-border))]"
              : "text-[hsl(var(--color-text-muted))] hover:text-white hover:bg-[hsl(var(--color-surface-2))]"
          }`}
        >
          <ClipboardList className="h-4 w-4 text-blue-400" />
          Service Queue
        </Link>
        <Link
          href="/mechanic/saathi"
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium transition-all ${
            isGrowth
              ? "bg-blue-500/15 text-blue-300 border border-blue-500/40 shadow-sm shadow-blue-500/10"
              : "text-[hsl(var(--color-text-muted))] hover:text-white hover:bg-[hsl(var(--color-surface-2))]"
          }`}
        >
          <Award className="h-4 w-4 text-blue-400" />
          <span>Mechanic Growth</span>
        </Link>
      </nav>

      {/* Mobile Nav */}
      <div className="md:hidden flex border-t border-[hsl(var(--color-border))] px-4 py-2 gap-2 bg-[hsl(var(--color-surface-2))]">
        <Link
          href="/mechanic/dashboard"
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium rounded-lg ${
            isQueue ? "bg-blue-600 text-white" : "text-[hsl(var(--color-text-muted))]"
          }`}
        >
          <ClipboardList className="h-3.5 w-3.5" />
          Service Queue
        </Link>
        <Link
          href="/mechanic/saathi"
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium rounded-lg ${
            isGrowth ? "bg-blue-600 text-white" : "text-[hsl(var(--color-text-muted))]"
          }`}
        >
          <Award className="h-3.5 w-3.5" />
          Mechanic Growth
        </Link>
      </div>
    </>
  );
}

export default function MechanicLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!user || user.role !== "MECHANIC")) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (!loading && (!user || user.role !== "MECHANIC")) {
    return <div className="p-8 text-center" role="status">Redirecting to sign in...</div>;
  }

  return (
    <div className="min-h-screen flex flex-col bg-[hsl(var(--color-surface))]">
      <header className="border-b border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface))] sticky top-0 z-40 backdrop-blur">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/mechanic/dashboard" className="flex items-center gap-2 group">
              <div className="w-9 h-9 rounded-xl bg-orange-500/10 border border-orange-500/30 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Wrench className="h-5 w-5 text-orange-400" />
              </div>
              <div>
                <span className="font-bold text-lg tracking-tight text-white">GripWise</span>
                <span className="ml-1 text-xs px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-300 font-medium">
                  Workshop
                </span>
              </div>
            </Link>

            <Suspense fallback={<div className="h-9 w-48" />}>
              <MechanicNavLinks />
            </Suspense>
          </div>

          <div className="flex items-center gap-5">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-xs text-[hsl(var(--color-text-muted))]">Authorized Workshop</span>
              <span className="font-medium text-sm text-white">{user?.display_name ?? "Restoring account..."}</span>
            </div>
            {user && (
              <button
                onClick={() => {
                  logout();
                  router.push("/login");
                }}
                className="text-[hsl(var(--color-text-muted))] hover:text-white transition-colors flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-[hsl(var(--color-border))] hover:bg-[hsl(var(--color-surface-2))]"
              >
                <LogOut className="h-3.5 w-3.5" />
                Sign Out
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
