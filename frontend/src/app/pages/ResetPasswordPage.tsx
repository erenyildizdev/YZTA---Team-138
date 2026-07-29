import {
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  AlertTriangle,
  CheckCircle2,
  KeyRound,
} from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router";

import { AuthCodeInput } from "../components/auth/AuthCodeInput";
import { AuthPageShell } from "../components/auth/AuthPageShell";
import { PasswordInput } from "../components/auth/PasswordInput";
import { Alert, AlertDescription } from "../components/ui/alert";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { useAuth } from "../context/AuthContext";
import {
  getEmailValidationError,
  hasFieldErrors,
  isApiErrorStatus,
  parseApiFieldErrors,
  SIX_ASCII_DIGIT_CODE,
  TOO_MANY_REQUESTS_MESSAGE,
  type FieldErrors,
} from "../lib/authForm";
import { confirmPasswordReset } from "../lib/api";

const RESET_SUCCESS_MESSAGE =
  "Parolanız yenilendi. Yeni parolanızla giriş yapın.";
const RESET_CODE_FAILURE_MESSAGE =
  "Parola sıfırlama kodu geçersiz veya süresi dolmuş.";

type ResetField =
  | "email"
  | "code"
  | "new_password"
  | "new_password_confirm";

interface ResetPasswordLocationState {
  email?: string;
  notice?: string;
}

export function ResetPasswordPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const locationState = location.state as ResetPasswordLocationState | null;
  const initialEmail =
    typeof locationState?.email === "string" ? locationState.email : "";
  const initialNotice =
    typeof locationState?.notice === "string" ? locationState.notice : null;

  const [email, setEmail] = useState(initialEmail);
  const [emailIsValid, setEmailIsValid] = useState(Boolean(initialEmail));
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [noticeMessage, setNoticeMessage] = useState<string | null>(
    initialNotice,
  );
  const [fieldErrors, setFieldErrors] = useState<FieldErrors<ResetField>>({});
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

  const clearFieldError = (field: ResetField) => {
    setFieldErrors((current) => ({ ...current, [field]: undefined }));
    setGeneralError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitInFlightRef.current || isSubmitting) {
      return;
    }

    const clientErrors: FieldErrors<ResetField> = {};
    const emailError = getEmailValidationError(email, emailIsValid);
    if (emailError) {
      clientErrors.email = emailError;
    }
    if (!SIX_ASCII_DIGIT_CODE.test(code)) {
      clientErrors.code = "Kod tam olarak altı rakamdan oluşmalıdır.";
    }
    if (!newPassword) {
      clientErrors.new_password = "Yeni parola gereklidir.";
    }
    if (!newPasswordConfirm) {
      clientErrors.new_password_confirm =
        "Yeni parola tekrarı gereklidir.";
    } else if (newPassword && newPassword !== newPasswordConfirm) {
      clientErrors.new_password_confirm = "Yeni parolalar eşleşmiyor.";
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
      await confirmPasswordReset({
        email: email.trim(),
        code,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      });
      if (!mountedRef.current) {
        return;
      }

      logout();
      navigate("/login", {
        replace: true,
        state: { successMessage: RESET_SUCCESS_MESSAGE },
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
        [
          "email",
          "code",
          "new_password",
          "new_password_confirm",
        ] as const,
      );
      if (hasFieldErrors(apiFieldErrors)) {
        setFieldErrors(apiFieldErrors);
      } else if (isApiErrorStatus(error, 400)) {
        setFieldErrors({ code: RESET_CODE_FAILURE_MESSAGE });
      } else {
        setGeneralError(
          "Parola şu anda yenilenemedi. Lütfen tekrar deneyin.",
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
      subtitle="Yeni parolanı belirle"
      footer={
        <p className="mt-5 text-center text-xs text-muted-foreground">
          Yeni bir kod mu gerekiyor?{" "}
          <Link
            to="/forgot-password"
            className="font-semibold text-primary hover:text-primary-hover"
          >
            Tekrar Gönder
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
              Parola sıfırlama
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              E-posta adresini, altı haneli kodu ve yeni parolanı gir.
            </p>
          </div>

          {noticeMessage && (
            <Alert
              role="status"
              aria-live="polite"
              className="border-success/30 bg-success/10 text-success"
            >
              <CheckCircle2 aria-hidden="true" />
              <AlertDescription className="text-success">
                {noticeMessage}
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <label
              htmlFor="reset-password-email"
              className="block text-xs font-semibold text-muted-foreground"
            >
              E-posta
            </label>
            <Input
              id="reset-password-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              autoFocus={!initialEmail}
              disabled={isSubmitting}
              value={email}
              onChange={(event) => {
                setEmail(event.currentTarget.value);
                setEmailIsValid(event.currentTarget.validity.valid);
                clearFieldError("email");
                setNoticeMessage(null);
              }}
              placeholder="ornek@eposta.com"
              aria-invalid={Boolean(fieldErrors.email)}
              aria-describedby={
                fieldErrors.email ? "reset-password-email-error" : undefined
              }
              className="h-auto rounded-xl border-border bg-muted px-3.5 py-2.5 text-sm text-foreground focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/20 dark:bg-muted"
            />
            {fieldErrors.email && (
              <p
                id="reset-password-email-error"
                role="alert"
                className="break-words text-xs leading-relaxed text-destructive"
              >
                {fieldErrors.email}
              </p>
            )}
          </div>

          <AuthCodeInput
            id="reset-password-code"
            value={code}
            onChange={(nextCode) => {
              setCode(nextCode);
              clearFieldError("code");
            }}
            disabled={isSubmitting}
            error={fieldErrors.code}
            autoFocus={Boolean(initialEmail)}
          />

          <div className="space-y-1.5">
            <label
              htmlFor="reset-password-new"
              className="block text-xs font-semibold text-muted-foreground"
            >
              Yeni parola
            </label>
            <PasswordInput
              id="reset-password-new"
              name="new_password"
              autoComplete="new-password"
              required
              disabled={isSubmitting}
              value={newPassword}
              onChange={(event) => {
                setNewPassword(event.currentTarget.value);
                clearFieldError("new_password");
                clearFieldError("new_password_confirm");
              }}
              placeholder="Yeni parolanız"
              aria-invalid={Boolean(fieldErrors.new_password)}
              aria-describedby={
                fieldErrors.new_password
                  ? "reset-password-new-error"
                  : undefined
              }
            />
            {fieldErrors.new_password && (
              <p
                id="reset-password-new-error"
                role="alert"
                className="break-words text-xs leading-relaxed text-destructive"
              >
                {fieldErrors.new_password}
              </p>
            )}
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="reset-password-confirm"
              className="block text-xs font-semibold text-muted-foreground"
            >
              Yeni parola (Tekrar)
            </label>
            <PasswordInput
              id="reset-password-confirm"
              name="new_password_confirm"
              autoComplete="new-password"
              required
              disabled={isSubmitting}
              value={newPasswordConfirm}
              onChange={(event) => {
                setNewPasswordConfirm(event.currentTarget.value);
                clearFieldError("new_password_confirm");
              }}
              placeholder="Yeni parolanızı tekrar girin"
              aria-invalid={Boolean(fieldErrors.new_password_confirm)}
              aria-describedby={
                fieldErrors.new_password_confirm
                  ? "reset-password-confirm-error"
                  : undefined
              }
            />
            {fieldErrors.new_password_confirm && (
              <p
                id="reset-password-confirm-error"
                role="alert"
                className="break-words text-xs leading-relaxed text-destructive"
              >
                {fieldErrors.new_password_confirm}
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
            <KeyRound aria-hidden="true" />
            {isSubmitting ? "Parola yenileniyor..." : "Parolayı Yenile"}
          </Button>
        </form>
      </Card>
    </AuthPageShell>
  );
}
