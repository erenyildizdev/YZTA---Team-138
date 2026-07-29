import {
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { Link, useNavigate } from "react-router";
import { AlertTriangle, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { ThemeToggle } from "../components/common/ThemeToggle";
import { PasswordInput } from "../components/auth/PasswordInput";
import {
  hasFieldErrors,
  isApiErrorStatus,
  parseApiFieldErrors,
  TOO_MANY_REQUESTS_MESSAGE,
  type FieldErrors,
} from "../lib/authForm";

const PASSWORD_LENGTH_ERROR = "Parola en az 8 karakter olmalı.";
const PASSWORD_MISMATCH_ERROR = "Parolalar eşleşmiyor.";
const REGISTER_DELIVERY_ERROR =
  "Doğrulama e-postası gönderilemedi ve kayıt tamamlanamadı. Lütfen daha sonra tekrar deneyin.";

type RegisterField =
  | "first_name"
  | "last_name"
  | "email"
  | "password"
  | "password_confirm";

export function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [fieldErrors, setFieldErrors] = useState<
    FieldErrors<RegisterField>
  >({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const mountedRef = useRef(false);
  const submitInFlightRef = useRef(false);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (isAuthenticated) navigate("/", { replace: true });
  }, [isAuthenticated, navigate]);

  const clearFieldError = (field: RegisterField) => {
    setFieldErrors((current) => ({ ...current, [field]: undefined }));
    setGeneralError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitInFlightRef.current || isSubmitting) {
      return;
    }

    const clientErrors: FieldErrors<RegisterField> = {};

    if (password.length < 8) {
      clientErrors.password = PASSWORD_LENGTH_ERROR;
    }
    if (password !== passwordConfirm) {
      clientErrors.password_confirm = PASSWORD_MISMATCH_ERROR;
    }

    if (hasFieldErrors(clientErrors)) {
      setFieldErrors(clientErrors);
      setGeneralError(null);
      return;
    }

    submitInFlightRef.current = true;
    setIsSubmitting(true);
    setFieldErrors({});
    setGeneralError(null);

    try {
      const response = await register({
        email,
        password,
        firstName,
        lastName,
      });
      if (!mountedRef.current) {
        return;
      }

      navigate("/verify-email", {
        replace: true,
        state: {
          email: response.email,
          notice: response.detail,
        },
      });
    } catch (error) {
      if (!mountedRef.current) {
        return;
      }

      if (isApiErrorStatus(error, 429)) {
        setGeneralError(TOO_MANY_REQUESTS_MESSAGE);
        return;
      }
      if (isApiErrorStatus(error, 503)) {
        setGeneralError(REGISTER_DELIVERY_ERROR);
        return;
      }

      const apiFieldErrors = parseApiFieldErrors(
        error,
        ["first_name", "last_name", "email", "password"] as const,
      );
      if (hasFieldErrors(apiFieldErrors)) {
        setFieldErrors(apiFieldErrors);
      } else {
        setGeneralError(
          "Kayıt şu anda tamamlanamadı. Lütfen tekrar deneyin.",
        );
      }
    } finally {
      submitInFlightRef.current = false;
      if (mountedRef.current) {
        setIsSubmitting(false);
      }
    }
  };

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
          aria-busy={isSubmitting}
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
                disabled={isSubmitting}
                value={firstName}
                onChange={(event) => {
                  setFirstName(event.currentTarget.value);
                  clearFieldError("first_name");
                }}
                placeholder="Ahmet"
                aria-invalid={Boolean(fieldErrors.first_name)}
                aria-describedby={
                  fieldErrors.first_name
                    ? "register-first-name-error"
                    : undefined
                }
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
              {fieldErrors.first_name && (
                <p
                  id="register-first-name-error"
                  role="alert"
                  className="break-words text-xs leading-relaxed text-destructive"
                >
                  {fieldErrors.first_name}
                </p>
              )}
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
                disabled={isSubmitting}
                value={lastName}
                onChange={(event) => {
                  setLastName(event.currentTarget.value);
                  clearFieldError("last_name");
                }}
                placeholder="Yılmaz"
                aria-invalid={Boolean(fieldErrors.last_name)}
                aria-describedby={
                  fieldErrors.last_name
                    ? "register-last-name-error"
                    : undefined
                }
                className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
              {fieldErrors.last_name && (
                <p
                  id="register-last-name-error"
                  role="alert"
                  className="break-words text-xs leading-relaxed text-destructive"
                >
                  {fieldErrors.last_name}
                </p>
              )}
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
              disabled={isSubmitting}
              value={email}
              onChange={(event) => {
                setEmail(event.currentTarget.value);
                clearFieldError("email");
              }}
              placeholder="ornek@eposta.com"
              aria-invalid={Boolean(fieldErrors.email)}
              aria-describedby={
                fieldErrors.email ? "register-email-error" : undefined
              }
              className="w-full bg-muted border border-border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
            />
            {fieldErrors.email && (
              <p
                id="register-email-error"
                role="alert"
                className="break-words text-xs leading-relaxed text-destructive"
              >
                {fieldErrors.email}
              </p>
            )}
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
                disabled={isSubmitting}
                value={password}
                onChange={(event) => {
                  setPassword(event.currentTarget.value);
                  clearFieldError("password");
                  clearFieldError("password_confirm");
                }}
                placeholder="••••••••"
                aria-invalid={Boolean(fieldErrors.password)}
                aria-describedby={
                  fieldErrors.password
                    ? "register-password-error"
                    : undefined
                }
              />
              {fieldErrors.password && (
                <p
                  id="register-password-error"
                  role="alert"
                  className="break-words text-xs leading-relaxed text-destructive"
                >
                  {fieldErrors.password}
                </p>
              )}
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
                disabled={isSubmitting}
                value={passwordConfirm}
                onChange={(event) => {
                  setPasswordConfirm(event.currentTarget.value);
                  clearFieldError("password_confirm");
                }}
                placeholder="••••••••"
                aria-invalid={Boolean(fieldErrors.password_confirm)}
                aria-describedby={
                  fieldErrors.password_confirm
                    ? "register-password-confirm-error"
                    : undefined
                }
              />
              {fieldErrors.password_confirm && (
                <p
                  id="register-password-confirm-error"
                  role="alert"
                  className="break-words text-xs leading-relaxed text-destructive"
                >
                  {fieldErrors.password_confirm}
                </p>
              )}
            </div>
          </div>

          {generalError && (
            <div
              role="alert"
              aria-live="assertive"
              className="flex items-start gap-2 bg-destructive/10 border border-destructive/30 rounded-xl px-3 py-2.5"
            >
              <AlertTriangle size={13} className="text-destructive mt-0.5 flex-shrink-0" />
              <p className="text-xs text-destructive leading-relaxed">
                {generalError}
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl py-2.5 text-sm font-semibold transition-all disabled:opacity-50"
          >
            {isSubmitting ? "Hesap oluşturuluyor..." : "Kayıt Ol"}
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
