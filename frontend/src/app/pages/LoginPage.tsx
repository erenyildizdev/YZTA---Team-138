import { type FormEvent, useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { AlertTriangle, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { ThemeToggle } from "../components/common/ThemeToggle";

export function LoginPage() {
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [authMessage, setAuthMessage] = useState<string | null>(null);

  const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? "/";

  useEffect(() => {
    if (isAuthenticated) navigate(from, { replace: true });
  }, [isAuthenticated, navigate, from]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (isLoading) return;
    const ok = await login(email, password);
    if (ok) navigate(from, { replace: true });
  };

  useEffect(() => {
    const message = sessionStorage.getItem("auth_message");

    if (message) {
      setAuthMessage(message);
      sessionStorage.removeItem("auth_message");
    }
  }, []);

  return (
    <div className="relative flex min-h-dvh w-full items-center justify-center bg-background px-4" style={{ animation: "page-in 0.3s ease-out" }}>
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
          className="bg-card border border-border rounded-2xl p-6 space-y-4"
        >
          {authMessage && (
            <div className="flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-3 py-2.5">
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
            <label className="text-xs font-semibold text-muted-foreground">E-posta</label>
            <input
              type="email"
              required
              autoFocus
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearError(); }}
              placeholder="ornek@eposta.com"
              className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground">Parola</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => { setPassword(e.target.value); clearError(); }}
              placeholder="••••••••"
              className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
            />
          </div>

          {error && (
            <div className="flex items-start gap-2 bg-destructive/10 border border-destructive/30 rounded-xl px-3 py-2.5">
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
