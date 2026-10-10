"use client";
import React, { createContext, useContext, useEffect, useState } from "react";
import type { UserRole } from "@/lib/types";

interface AuthUser {
  user_id: string;
  role: UserRole;
  display_name: string;
  access_token: string;
  refresh_token: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  setUser: (u: AuthUser | null) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  setUser: () => {},
  logout: () => {},
  loading: true,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("gw_user");
      if (stored) setUserState(JSON.parse(stored));
    } catch {}
    setLoading(false);
  }, []);

  const setUser = (u: AuthUser | null) => {
    setUserState(u);
    if (u) localStorage.setItem("gw_user", JSON.stringify(u));
    else localStorage.removeItem("gw_user");
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, setUser, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
