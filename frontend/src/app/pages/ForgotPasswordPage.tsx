import {
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { AlertTriangle, Mail } from "lucide-react";
import { Link, useNavigate } from "react-router";

import { AuthPageShell } from "../components/auth/AuthPageShell";
import { Alert, AlertDescription } from "../components/ui/alert";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import {
  getEmailValidationError,
  hasFieldErrors,
  isApiErrorStatus,
  parseApiFieldErrors,
  TOO_MANY_REQUESTS_MESSAGE,
} from "../lib/authForm";
import { requestPasswordReset } from "../lib/api";

const PASSWORD_RESET_REQUEST_MESSAGE =
  "E-posta adresi uygunsa parola sıfırlama kodu gönderildi.";

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [emailIsValid, setEmailIsValid] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
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

  const validateEmail = (): string | null =>
    getEmailValidationError(email, emailIsValid);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitInFlightRef.current || isSubmitting) {
      return;
    }

    const clientEmailError = validateEmail();
    if (clientEmailError) {
      setEmailError(clientEmailError);
      setGeneralError(null);
      return;
    }

    submitInFlightRef.current = true;
    setIsSubmitting(true);
    setEmailError(null);
    setGeneralError(null);

    try {
      await requestPasswordReset({ email: email.trim() });
      if (!mountedRef.current) {
        return;
      }

      navigate("/reset-password", {
        state: {
          email: email.trim(),
          notice: PASSWORD_RESET_REQUEST_MESSAGE,
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

      const apiFieldErrors = parseApiFieldErrors(
        error,
        ["email"] as const,
      );
      if (hasFieldErrors(apiFieldErrors)) {
        setEmailError(apiFieldErrors.email ?? null);
      } else {
        setGeneralError(
          "Parola sıfırlama isteği şu anda gönderilemedi. Lütfen tekrar deneyin.",
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
    <AuthPageShell
      subtitle="Parolanı sıfırla"
      footer={
        <p className="mt-5 text-center text-xs text-muted-foreground">
          Parolanı hatırladın mı?{" "}
          <Link
            to="/login"
            className="font-semibold text-primary hover:text-primary-hover"
          >
            Giriş Yap
          </Link>
        </p>
      }
    >
      <Card className="gap-0 rounded-2xl p-6">
        <form
          noValidate
          onSubmit={handleSubmit}
          aria-busy={isSubmitting}
          className="space-y-4"
        >
          <div>
            <h2 className="text-base font-semibold text-foreground">
              Şifremi unuttum
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              E-posta adresini gir. Adres uygunsa parola sıfırlama kodu
              gönderilir.
            </p>
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="forgot-password-email"
              className="block text-xs font-semibold text-muted-foreground"
            >
              E-posta
            </label>
            <Input
              id="forgot-password-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              autoFocus
              disabled={isSubmitting}
              value={email}
              onChange={(event) => {
                setEmail(event.currentTarget.value);
                setEmailIsValid(event.currentTarget.validity.valid);
                setEmailError(null);
                setGeneralError(null);
              }}
              onBlur={() => {
                const clientEmailError = validateEmail();
                if (clientEmailError) {
                  setEmailError(clientEmailError);
                }
              }}
              placeholder="ornek@eposta.com"
              aria-invalid={Boolean(emailError)}
              aria-describedby={
                emailError ? "forgot-password-email-error" : undefined
              }
              className="h-auto rounded-xl border-border bg-muted px-3.5 py-2.5 text-sm text-foreground focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/20 dark:bg-muted"
            />
            {emailError && (
              <p
                id="forgot-password-email-error"
                role="alert"
                className="break-words text-xs leading-relaxed text-destructive"
              >
                {emailError}
              </p>
            )}
          </div>

          {generalError && (
            <Alert variant="destructive" aria-live="assertive">
              <AlertTriangle aria-hidden="true" />
              <AlertDescription>{generalError}</AlertDescription>
            </Alert>
          )}

          <Button
            type="submit"
            disabled={isSubmitting}
            className="h-auto w-full rounded-xl py-2.5"
          >
            <Mail aria-hidden="true" />
            {isSubmitting ? "Gönderiliyor..." : "Sıfırlama Kodu Gönder"}
          </Button>
        </form>
      </Card>
    </AuthPageShell>
  );
}
