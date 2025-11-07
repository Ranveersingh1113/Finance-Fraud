import { createContext, useCallback, useContext, useEffect, useMemo, useState, ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { updateApiClientKey, getCurrentApiClientKey } from "@/lib/api-client";
import { userApi } from "@/services/api";

interface AuthContextValue {
  isAuthenticated: boolean;
  isInitializing: boolean;
  user: any | null;
  login: (apiKey: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const queryClient = useQueryClient();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [user, setUser] = useState<any | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") {
      setIsInitializing(false);
      return;
    }

    const STORAGE_KEY = "finance_fraud_api_key" as const;
    const sessionKey = window.sessionStorage?.getItem(STORAGE_KEY) ?? null;
    const legacyKey = window.localStorage?.getItem(STORAGE_KEY) ?? null;
    const storedKey = sessionKey || legacyKey;

    if (storedKey) {
      updateApiClientKey(storedKey);
      window.localStorage?.removeItem(STORAGE_KEY);
      window.sessionStorage?.setItem(STORAGE_KEY, storedKey);
      setIsAuthenticated(true);
      userApi
        .getProfile()
        .then((profile) => {
          setUser(profile);
          queryClient.setQueryData(["user", "profile"], profile);
        })
        .catch(() => {
          updateApiClientKey(null);
          localStorage.removeItem("finance_fraud_api_key");
          setIsAuthenticated(false);
        })
        .finally(() => setIsInitializing(false));
    } else {
      updateApiClientKey(null);
      window.localStorage?.removeItem(STORAGE_KEY);
      setIsInitializing(false);
    }
  }, [queryClient]);

  const login = useCallback(async (apiKey: string) => {
    const previousKey = getCurrentApiClientKey();
    updateApiClientKey(apiKey);
    try {
      const profile = await userApi.getProfile();
      setUser(profile);
      setIsAuthenticated(true);
      queryClient.setQueryData(["user", "profile"], profile);
    } catch (error) {
      updateApiClientKey(previousKey || null);
      throw error;
    }
  }, [queryClient]);

  const logout = useCallback(() => {
    updateApiClientKey(null);
    setIsAuthenticated(false);
    setUser(null);
    queryClient.removeQueries({ queryKey: ["user"] });
  }, [queryClient]);

  const value = useMemo(
    () => ({ isAuthenticated, isInitializing, user, login, logout }),
    [isAuthenticated, isInitializing, login, logout, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

