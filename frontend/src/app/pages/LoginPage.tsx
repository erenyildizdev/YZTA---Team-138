import { type FormEvent, useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { AlertTriangle, CheckCircle2, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { ThemeToggle } from "../components/common/ThemeToggle";
import { PasswordInput } from "../components/auth/PasswordInput";

const PASSWORD_CHANGE_MESSAGE_KEY = "password_change_message";

interface LoginLocationState {
  from?: { pathname: string };
  passwordChangeMessage?: string;
}

export function LoginPage() {
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const submitInFlightRef = useRef(false);

  const [authMessage, setAuthMessage] = useState<string | null>(null);
  const locationState = location.state as LoginLocationState | null;
  const [passwordChangeMessage, setPasswordChangeMessage] =
    useState<string | null>(
      locationState?.passwordChangeMessage ?? null,
    );

  const from = passwordChangeMessage
    ? "/"
    : locationState?.from?.pathname ?? "/";

  useEffect(() => {
    if (!locationState?.passwordChangeMessage) {
      return;
    }

    const preservedState = locationState.from
      ? { from: locationState.from }
      : null;

    navigate(
      `${location.pathname}${location.search}${location.hash}`,
      {
        replace: true,
        state: preservedState,
      },
    );
  }, [
    location.hash,
    location.pathname,
    location.search,
    locationState,
    navigate,
  ]);

  useEffect(() => {
    if (isAuthenticated) navigate(from, { replace: true });
  }, [isAuthenticated, navigate, from]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (submitInFlightRef.current || isLoading) return;
    submitInFlightRef.current = true;

    try {
      await login(email, password);
    } finally {
      submitInFlightRef.current = false;
    }
  };

  useEffect(() => {
    let reauthenticationMessage: string | null = null;
    let authenticationMessage: string | null = null;

    try {
      reauthenticationMessage = sessionStorage.getItem(
        PASSWORD_CHANGE_MESSAGE_KEY,
      );
      authenticationMessage =
        sessionStorage.getItem("auth_message");
      sessionStorage.removeItem(PASSWORD_CHANGE_MESSAGE_KEY);
      sessionStorage.removeItem("auth_message");
    } catch {
      // Storage notices are best-effort; login itself remains available.
    }

    if (!passwordChangeMessage && reauthenticationMessage) {
      setPasswordChangeMessage(reauthenticationMessage);
      return;
    }

    if (!passwordChangeMessage && authenticationMessage) {
      setAuthMessage(authenticationMessage);
    }
  }, []);

  return (
    <div className="relative flex min-h-dvh w-full animate-[page-in_0.3s_ease-out] items-center justify-center bg-background px-4">
      <ThemeToggle className="absolute top-4 right-4" />
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-7">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary mb-3">
            <Sparkles size={20} className="text-primary-foreground" />
          </span>
          <h1 className="text-lg font-bold text-foreground">FikirLab</h1>
          <p className="text-sm text-muted-foreground mt-1">Tekrar hoş geldin</p>
        </div>

        <form
          onSubmit={handleSubmit}
          aria-busy={isLoading}
          className="bg-card border border-border rounded-2xl p-6 space-y-4"
        >
          {passwordChangeMessage && (
            <div
              role="status"
              aria-live="polite"
              className="flex items-start gap-2 rounded-xl border border-success/30 bg-success/10 px-3 py-2.5"
            >
              <CheckCircle2
                aria-hidden="true"
                size={13}
                className="mt-0.5 flex-shrink-0 text-success"
              />

              <p className="text-xs leading-relaxed text-success">
                {passwordChangeMessage}
              </p>
            </div>
          )}

          {authMessage && (
            <div
              role="alert"
              aria-live="assertive"
              className="flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-3 py-2.5"
            >
              <AlertTriangle
                size={13}
                className="mt-0.5 flex-shrink-0 text-destructive"
              />

              <p className="text-xs leading-relaxed text-destructive">
                {authMessage}
              </p>
            </div>
          )}
          <div className="space-y-1.5">
            <label
              htmlFor="login-email"
              className="text-xs font-semibold text-muted-foreground"
            >
              E-posta
            </label>
            <input
              id="login-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              autoFocus
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearError(); }}
              placeholder="ornek@eposta.com"
              className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="login-password"
              className="text-xs font-semibold text-muted-foreground"
            >
              Parola
            </label>
            <PasswordInput
              id="login-password"
              name="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => { setPassword(e.target.value); clearError(); }}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div
              role="alert"
              aria-live="assertive"
              className="flex items-start gap-2 bg-destructive/10 border border-destructive/30 rounded-xl px-3 py-2.5"
            >
              <AlertTriangle size={13} className="text-destructive mt-0.5 flex-shrink-0" />
              <p className="text-xs text-destructive leading-relaxed">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl py-2.5 text-sm font-semibold transition-all disabled:opacity-50"
          >
            {isLoading ? "Giriş yapılıyor..." : "Giriş Yap"}
          </button>
        </form>

        <p className="text-center text-xs text-muted-foreground mt-5">
          Hesabın yok mu?{" "}
          <Link to="/register" className="text-primary hover:text-primary-hover font-semibold">
            Kayıt Ol
          </Link>
        </p>
      </div>
    </div>
  );
}
