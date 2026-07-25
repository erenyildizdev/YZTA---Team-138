import { type FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { AlertTriangle, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const { register, isAuthenticated, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) navigate("/", { replace: true });
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);

    if (password.length < 8) {
      setFormError("Parola en az 8 karakter olmalı.");
      return;
    }
    if (password !== passwordConfirm) {
      setFormError("Parolalar eşleşmiyor.");
      return;
    }

    const ok = await register({ email, password, firstName, lastName });
    if (ok) navigate("/", { replace: true });
  };

  const displayError = formError ?? error;

  return (
    <div className="flex min-h-dvh w-full items-center justify-center bg-background px-4 py-10" style={{ animation: "page-in 0.3s ease-out" }}>
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-7">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary mb-3">
            <Sparkles size={20} className="text-white" />
          </span>
          <h1 className="text-lg font-bold text-foreground">FikirLab</h1>
          <p className="text-sm text-muted-foreground mt-1">Hesap oluştur</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-card border border-border rounded-2xl p-6 space-y-4"
        >
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Ad</label>
              <input
                type="text"
                required
                autoFocus
                value={firstName}
                onChange={(e) => { setFirstName(e.target.value); clearError(); setFormError(null); }}
                placeholder="Ahmet"
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Soyad</label>
              <input
                type="text"
                required
                value={lastName}
                onChange={(e) => { setLastName(e.target.value); clearError(); setFormError(null); }}
                placeholder="Yılmaz"
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground">E-posta</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearError(); setFormError(null); }}
              placeholder="ornek@eposta.com"
              className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Parola</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => { setPassword(e.target.value); clearError(); setFormError(null); }}
                placeholder="••••••••"
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Parola (Tekrar)</label>
              <input
                type="password"
                required
                value={passwordConfirm}
                onChange={(e) => { setPasswordConfirm(e.target.value); clearError(); setFormError(null); }}
                placeholder="••••••••"
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
            </div>
          </div>

          {displayError && (
            <div className="flex items-start gap-2 bg-red-900/10 border border-red-800/30 rounded-xl px-3 py-2.5">
              <AlertTriangle size={13} className="text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-xs text-red-400 leading-relaxed">{displayError}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full inline-flex items-center justify-center gap-2 bg-primary hover:bg-blue-600 text-white rounded-xl py-2.5 text-sm font-semibold transition-all disabled:opacity-50"
          >
            {isLoading ? "Hesap oluşturuluyor..." : "Kayıt Ol"}
          </button>
        </form>

        <p className="text-center text-xs text-muted-foreground mt-5">
          Zaten hesabın var mı?{" "}
          <Link to="/login" className="text-blue-400 hover:text-blue-300 font-semibold">
            Giriş Yap
          </Link>
        </p>
      </div>
    </div>
  );
}
