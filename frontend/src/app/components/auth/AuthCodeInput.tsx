import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "../ui/input-otp";
import { sanitizeAuthCode } from "../../lib/authForm";

interface AuthCodeInputProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: string;
  autoFocus?: boolean;
}

const CODE_SLOT_INDEXES = [0, 1, 2, 3, 4, 5] as const;

export function AuthCodeInput({
  id,
  value,
  onChange,
  disabled = false,
  error,
  autoFocus = false,
}: AuthCodeInputProps) {
  const errorId = `${id}-error`;

  return (
    <div className="min-w-0 space-y-1.5">
      <label
        htmlFor={id}
        className="block text-xs font-semibold text-muted-foreground"
      >
        Altı haneli doğrulama kodu
      </label>

      <InputOTP
        id={id}
        name="code"
        value={value}
        onChange={(nextValue) => onChange(sanitizeAuthCode(nextValue))}
        maxLength={6}
        inputMode="numeric"
        autoComplete="one-time-code"
        pattern="^[0-9]*$"
        required
        disabled={disabled}
        autoFocus={autoFocus}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        containerClassName="w-full justify-center overflow-hidden"
      >
        <InputOTPGroup>
          {CODE_SLOT_INDEXES.map((index) => (
            <InputOTPSlot
              key={index}
              index={index}
              aria-invalid={Boolean(error)}
              className="h-9 w-9 sm:h-10 sm:w-10"
            />
          ))}
        </InputOTPGroup>
      </InputOTP>

      {error && (
        <p
          id={errorId}
          role="alert"
          className="break-words text-xs leading-relaxed text-destructive"
        >
          {error}
        </p>
      )}
    </div>
  );
}
