"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { LogOut, Wrench } from "lucide-react";

export default function MechanicLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!user || user.role !== "MECHANIC")) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading || !user || user.role !== "MECHANIC") return null;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface))]">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wrench className="h-6 w-6 text-orange-500" />
            <span className="font-bold text-xl tracking-tight">GripWise <span className="text-[hsl(var(--color-text-muted))] font-normal">Mechanic</span></span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="text-sm">
              <span className="text-[hsl(var(--color-text-muted))]">Workshop: </span>
              <span className="font-medium text-white">{user.display_name}</span>
            </div>
            <button 
              onClick={() => { logout(); router.push("/login"); }}
              className="text-[hsl(var(--color-text-muted))] hover:text-white transition-colors flex items-center gap-2 text-sm"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </button>
          </div>
        </div>
      </header>
      
      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}
