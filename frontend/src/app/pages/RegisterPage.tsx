import { type FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { AlertTriangle, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { ThemeToggle } from "../components/common/ThemeToggle";
import { PasswordInput } from "../components/auth/PasswordInput";

const PASSWORD_LENGTH_ERROR = "Parola en az 8 karakter olmalı.";
const PASSWORD_MISMATCH_ERROR = "Parolalar eşleşmiyor.";

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
    if (isLoading) return;
    setFormError(null);

    if (password.length < 8) {
      setFormError(PASSWORD_LENGTH_ERROR);
      return;
    }
    if (password !== passwordConfirm) {
      setFormError(PASSWORD_MISMATCH_ERROR);
      return;
    }

    const ok = await register({ email, password, firstName, lastName });
    if (ok) navigate("/", { replace: true });
  };

  const displayError = formError ?? error;
  const formErrorField =
    formError === PASSWORD_LENGTH_ERROR
      ? "password"
      : formError === PASSWORD_MISMATCH_ERROR
        ? "password_confirm"
        : null;

  return (
    <div className="relative flex min-h-dvh w-full animate-[page-in_0.3s_ease-out] items-center justify-center bg-background px-4 py-10">
      <ThemeToggle className="absolute top-4 right-4" />
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-7">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary mb-3">
            <Sparkles size={20} className="text-primary-foreground" />
          </span>
          <h1 className="text-lg font-bold text-foreground">FikirLab</h1>
          <p className="text-sm text-muted-foreground mt-1">Hesap oluştur</p>
        </div>

        <form
          onSubmit={handleSubmit}
          aria-busy={isLoading}
          className="bg-card border border-border rounded-2xl p-6 space-y-4"
        >
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label
                htmlFor="register-first-name"
                className="text-xs font-semibold text-muted-foreground"
              >
                Ad
              </label>
              <input
                id="register-first-name"
                name="first_name"
                type="text"
                autoComplete="given-name"
                required
                autoFocus
                value={firstName}
                onChange={(e) => { setFirstName(e.target.value); clearError(); setFormError(null); }}
                placeholder="Ahmet"
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label
                htmlFor="register-last-name"
                className="text-xs font-semibold text-muted-foreground"
              >
                Soyad
              </label>
              <input
                id="register-last-name"
                name="last_name"
                type="text"
                autoComplete="family-name"
                required
                value={lastName}
                onChange={(e) => { setLastName(e.target.value); clearError(); setFormError(null); }}
                placeholder="Yılmaz"
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="register-email"
              className="text-xs font-semibold text-muted-foreground"
            >
              E-posta
            </label>
            <input
              id="register-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearError(); setFormError(null); }}
              placeholder="ornek@eposta.com"
              className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
            />
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="min-w-0 space-y-1.5">
              <label
                htmlFor="register-password"
                className="text-xs font-semibold text-muted-foreground"
              >
                Parola
              </label>
              <PasswordInput
                id="register-password"
                name="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => { setPassword(e.target.value); clearError(); setFormError(null); }}
                placeholder="••••••••"
                aria-invalid={formErrorField === "password"}
                aria-describedby={
                  formErrorField === "password"
                    ? "register-form-error"
                    : undefined
                }
              />
            </div>
            <div className="min-w-0 space-y-1.5">
              <label
                htmlFor="register-password-confirm"
                className="text-xs font-semibold text-muted-foreground"
              >
                Parola (Tekrar)
              </label>
              <PasswordInput
                id="register-password-confirm"
                name="password_confirm"
                autoComplete="new-password"
                required
                value={passwordConfirm}
                onChange={(e) => { setPasswordConfirm(e.target.value); clearError(); setFormError(null); }}
                placeholder="••••••••"
                aria-invalid={formErrorField === "password_confirm"}
                aria-describedby={
                  formErrorField === "password_confirm"
                    ? "register-form-error"
                    : undefined
                }
              />
            </div>
          </div>

          {displayError && (
            <div
              id="register-form-error"
              role="alert"
              aria-live="assertive"
              className="flex items-start gap-2 bg-destructive/10 border border-destructive/30 rounded-xl px-3 py-2.5"
            >
              <AlertTriangle size={13} className="text-destructive mt-0.5 flex-shrink-0" />
              <p className="text-xs text-destructive leading-relaxed">{displayError}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl py-2.5 text-sm font-semibold transition-all disabled:opacity-50"
          >
            {isLoading ? "Hesap oluşturuluyor..." : "Kayıt Ol"}
          </button>
        </form>

        <p className="text-center text-xs text-muted-foreground mt-5">
          Zaten hesabın var mı?{" "}
          <Link to="/login" className="text-primary hover:text-primary-hover font-semibold">
            Giriş Yap
          </Link>
        </p>
      </div>
    </div>
  );
}
