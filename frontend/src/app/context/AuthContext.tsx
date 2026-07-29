import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  ApiError,
  getAccessToken,
  isEmailNotVerifiedErrorPayload,
  login as loginRequest,
  register as registerRequest,
  setAccessToken,
  type AuthUser,
  type EmailNotVerifiedErrorPayload,
  type RegisterVerificationResponse,
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

export type LoginResult =
  | { ok: true }
  | {
      ok: false;
      reason: "email_not_verified";
      payload: EmailNotVerifiedErrorPayload;
    }
  | { ok: false; reason: "error" | "cancelled" };

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<LoginResult>;
  cancelLogin: () => void;
  register: (input: RegisterInput) => Promise<RegisterVerificationResponse>;
  logout: () => void;
  clearError: () => void;
  updateUser: (user: AuthUser) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => readStoredUser());
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loginGenerationRef = useRef(0);

  const persistSession = (accessToken: string, authUser: AuthUser) => {
    const previousUser = readStoredUser();
    if (previousUser?.id !== authUser.id) clearActiveIdeaId();
    setAccessToken(accessToken);
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authUser));
    setToken(accessToken);
    setUser(authUser);
  };

  const login = async (email: string, password: string) => {
    const generation = loginGenerationRef.current + 1;
    loginGenerationRef.current = generation;
    setIsLoading(true);
    setError(null);
    try {
      const res = await loginRequest(email, password);
      if (generation !== loginGenerationRef.current) {
        return { ok: false, reason: "cancelled" } as const;
      }
      persistSession(res.access_token, res.user);
      return { ok: true } as const;
    } catch (err) {
      if (generation !== loginGenerationRef.current) {
        return { ok: false, reason: "cancelled" } as const;
      }

      if (
        err instanceof ApiError &&
        err.status === 403 &&
        isEmailNotVerifiedErrorPayload(err.data)
      ) {
        return {
          ok: false,
          reason: "email_not_verified",
          payload: err.data,
        } as const;
      }

      setError(err instanceof ApiError ? err.message : "Giriş yapılamadı.");
      return { ok: false, reason: "error" } as const;
    } finally {
      if (generation === loginGenerationRef.current) {
        setIsLoading(false);
      }
    }
  };

  const cancelLogin = useCallback(() => {
    loginGenerationRef.current += 1;
    setIsLoading(false);
    setError(null);
  }, []);

  const register = (input: RegisterInput) => {
    setError(null);
    return registerRequest({
      email: input.email,
      password: input.password,
      first_name: input.firstName,
      last_name: input.lastName,
    });
  };

  const logout = () => {
    loginGenerationRef.current += 1;
    clearActiveIdeaId();
    setAccessToken(null);
    localStorage.removeItem(USER_STORAGE_KEY);
    setToken(null);
    setUser(null);
  };

  const clearError = () => setError(null);

  const updateUser = (nextUser: AuthUser) => {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(nextUser));
    setUser(nextUser);
  };

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: !!token, isLoading, error, login, cancelLogin, register, logout, clearError, updateUser }),
    [user, token, isLoading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
