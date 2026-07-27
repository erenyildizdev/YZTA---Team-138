import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import {
  ApiError,
  getAccessToken,
  login as loginRequest,
  register as registerRequest,
  setAccessToken,
  type AuthUser,
} from "../lib/api";
import { clearActiveIdeaId } from "../hooks/useActiveIdeaId";

const USER_STORAGE_KEY = "fikirlab_user";

function readStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export interface RegisterInput {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (input: RegisterInput) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => readStoredUser());
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const persistSession = (accessToken: string, authUser: AuthUser) => {
    const previousUser = readStoredUser();
    if (previousUser?.id !== authUser.id) clearActiveIdeaId();
    setAccessToken(accessToken);
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authUser));
    setToken(accessToken);
    setUser(authUser);
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await loginRequest(email, password);
      persistSession(res.access_token, res.user);
      return true;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Giriş yapılamadı.");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (input: RegisterInput) => {
    setIsLoading(true);
    setError(null);
    try {
      await registerRequest({
        email: input.email,
        password: input.password,
        first_name: input.firstName,
        last_name: input.lastName,
      });
      const res = await loginRequest(input.email, input.password);
      persistSession(res.access_token, res.user);
      return true;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Kayıt oluşturulamadı.");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    clearActiveIdeaId();
    setAccessToken(null);
    localStorage.removeItem(USER_STORAGE_KEY);
    setToken(null);
    setUser(null);
  };

  const clearError = () => setError(null);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: !!token, isLoading, error, login, register, logout, clearError }),
    [user, token, isLoading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
