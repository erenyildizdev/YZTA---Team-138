import {
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  AlertTriangle,
  CheckCircle2,
  MailCheck,
} from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router";

import { AuthCodeInput } from "../components/auth/AuthCodeInput";
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
  SIX_ASCII_DIGIT_CODE,
  TOO_MANY_REQUESTS_MESSAGE,
  type FieldErrors,
} from "../lib/authForm";
import {
  resendEmailVerification,
  verifyEmail,
} from "../lib/api";

const VERIFY_SUCCESS_MESSAGE =
  "E-posta adresiniz doğrulandı. Şimdi giriş yapabilirsiniz.";
const VERIFY_FAILURE_MESSAGE =
  "Doğrulama kodu geçersiz veya süresi dolmuş.";
const RESEND_GENERIC_MESSAGE =
  "E-posta adresi uygunsa yeni doğrulama kodu gönderildi.";

type VerifyField = "email" | "code";

interface VerifyEmailLocationState {
  email?: string;
  notice?: string;
}

export function VerifyEmailPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const locationState = location.state as VerifyEmailLocationState | null;
  const initialEmail =
    typeof locationState?.email === "string" ? locationState.email : "";
  const initialNotice =
    typeof locationState?.notice === "string" ? locationState.notice : null;

  const [email, setEmail] = useState(initialEmail);
  const [emailIsValid, setEmailIsValid] = useState(Boolean(initialEmail));
  const [code, setCode] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors<VerifyField>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(
    initialNotice,
  );
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);

  const mountedRef = useRef(false);
  const verifyInFlightRef = useRef(false);
  const resendInFlightRef = useRef(false);

  const isBusy = isVerifying || isResending;

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!locationState?.email && !locationState?.notice) {
      return;
    }

    navigate(
      `${location.pathname}${location.search}${location.hash}`,
      { replace: true, state: null },
    );
  }, [
    location.hash,
    location.pathname,
    location.search,
    locationState?.email,
    locationState?.notice,
    navigate,
  ]);

  const clearFieldError = (field: VerifyField) => {
    setFieldErrors((current) => ({ ...current, [field]: undefined }));
    setGeneralError(null);
  };

  const validateEmail = (): string | null =>
    getEmailValidationError(email, emailIsValid);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (
      verifyInFlightRef.current ||
      resendInFlightRef.current ||
      isBusy
    ) {
      return;
    }

    const clientErrors: FieldErrors<VerifyField> = {};
    const emailError = validateEmail();
    if (emailError) {
      clientErrors.email = emailError;
    }
    if (!SIX_ASCII_DIGIT_CODE.test(code)) {
      clientErrors.code = "Kod tam olarak altı rakamdan oluşmalıdır.";
    }

    if (hasFieldErrors(clientErrors)) {
      setFieldErrors(clientErrors);
      setGeneralError(null);
      return;
    }

    verifyInFlightRef.current = true;
    setIsVerifying(true);
    setFieldErrors({});
    setGeneralError(null);
    setStatusMessage(null);

    try {
      await verifyEmail({ email: email.trim(), code });
      if (!mountedRef.current) {
        return;
      }

      navigate("/login", {
        replace: true,
        state: { successMessage: VERIFY_SUCCESS_MESSAGE },
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
        ["email", "code"] as const,
      );
      if (hasFieldErrors(apiFieldErrors)) {
        setFieldErrors(apiFieldErrors);
      } else if (isApiErrorStatus(error, 400)) {
        setFieldErrors({ code: VERIFY_FAILURE_MESSAGE });
      } else {
        setGeneralError(
          "E-posta doğrulaması şu anda tamamlanamadı. Lütfen tekrar deneyin.",
        );
      }
    } finally {
      verifyInFlightRef.current = false;
      if (mountedRef.current) {
        setIsVerifying(false);
      }
    }
  };

  const handleResend = async () => {
    if (
      verifyInFlightRef.current ||
      resendInFlightRef.current ||
      isBusy
    ) {
      return;
    }

    const emailError = validateEmail();
    if (emailError) {
      setFieldErrors((current) => ({ ...current, email: emailError }));
      setGeneralError(null);
      return;
    }

    resendInFlightRef.current = true;
    setIsResending(true);
    setFieldErrors((current) => ({ ...current, email: undefined }));
    setGeneralError(null);
    setStatusMessage(null);

    try {
      await resendEmailVerification({ email: email.trim() });
      if (mountedRef.current) {
        setStatusMessage(RESEND_GENERIC_MESSAGE);
      }
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
        setFieldErrors((current) => ({
          ...current,
          email: apiFieldErrors.email,
        }));
      } else {
        setGeneralError(
          "Kod gönderme isteği tamamlanamadı. Lütfen tekrar deneyin.",
        );
      }
    } finally {
      resendInFlightRef.current = false;
      if (mountedRef.current) {
        setIsResending(false);
      }
    }
  };

  return (
    <AuthPageShell
      subtitle="E-posta adresini doğrula"
      footer={
        <p className="mt-5 text-center text-xs text-muted-foreground">
          Giriş ekranına dönmek ister misin?{" "}
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
          aria-busy={isBusy}
          className="space-y-4"
        >
          <div>
            <h2 className="text-base font-semibold text-foreground">
              Doğrulama kodunu gir
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              E-posta adresine gönderilen altı haneli kodu kullan.
              Router bilgisi yoksa e-posta adresini elle girebilirsin.
            </p>
          </div>

          {statusMessage && (
            <Alert
              role="status"
              aria-live="polite"
              className="border-success/30 bg-success/10 text-success"
            >
              <CheckCircle2 aria-hidden="true" />
              <AlertDescription className="text-success">
                {statusMessage}
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <label
              htmlFor="verify-email"
              className="block text-xs font-semibold text-muted-foreground"
            >
              E-posta
            </label>
            <Input
              id="verify-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              disabled={isBusy}
              value={email}
              onChange={(event) => {
                setEmail(event.currentTarget.value);
                setEmailIsValid(event.currentTarget.validity.valid);
                clearFieldError("email");
                setStatusMessage(null);
              }}
              onBlur={() => {
                const emailError = validateEmail();
                if (emailError) {
                  setFieldErrors((current) => ({
                    ...current,
                    email: emailError,
                  }));
                }
              }}
              placeholder="ornek@eposta.com"
              aria-invalid={Boolean(fieldErrors.email)}
              aria-describedby={
                fieldErrors.email ? "verify-email-error" : undefined
              }
              className="h-auto rounded-xl border-border bg-muted px-3.5 py-2.5 text-sm text-foreground focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/20 dark:bg-muted"
            />
            {fieldErrors.email && (
              <p
                id="verify-email-error"
                role="alert"
                className="break-words text-xs leading-relaxed text-destructive"
              >
                {fieldErrors.email}
              </p>
            )}
          </div>

          <AuthCodeInput
            id="verify-code"
            value={code}
            onChange={(nextCode) => {
              setCode(nextCode);
              clearFieldError("code");
            }}
            disabled={isBusy}
            error={fieldErrors.code}
            autoFocus={Boolean(initialEmail)}
          />

          {generalError && (
            <Alert variant="destructive" aria-live="assertive">
              <AlertTriangle aria-hidden="true" />
              <AlertDescription>{generalError}</AlertDescription>
            </Alert>
          )}

          <Button
            type="submit"
            disabled={isBusy}
            className="h-auto w-full rounded-xl py-2.5"
          >
            <MailCheck aria-hidden="true" />
            {isVerifying ? "Doğrulanıyor..." : "E-postayı Doğrula"}
          </Button>

          <Button
            type="button"
            variant="outline"
            disabled={isBusy || !email.trim() || !emailIsValid}
            onClick={() => void handleResend()}
            className="h-auto w-full rounded-xl py-2.5"
          >
            {isResending ? "Gönderiliyor..." : "Kodu Yeniden Gönder"}
          </Button>
        </form>
      </Card>
    </AuthPageShell>
  );
}
