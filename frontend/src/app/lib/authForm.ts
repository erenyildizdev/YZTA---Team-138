import { ApiError } from "./api";

export type FieldErrors<Field extends string> = Partial<
  Record<Field, string>
>;

export const SIX_ASCII_DIGIT_CODE = /^[0-9]{6}$/;

export const TOO_MANY_REQUESTS_MESSAGE =
  "Çok fazla istek gönderildi. Lütfen daha sonra tekrar deneyin.";

export function sanitizeAuthCode(value: string): string {
  return value.replace(/[^0-9]/g, "").slice(0, 6);
}

export function getEmailValidationError(
  value: string,
  browserValidity: boolean,
): string | null {
  if (!value.trim()) {
    return "E-posta adresi gereklidir.";
  }
  if (!browserValidity) {
    return "Geçerli bir e-posta adresi girin.";
  }
  return null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function getErrorText(value: unknown): string | null {
  if (typeof value === "string" && value.trim()) {
    return value;
  }

  if (Array.isArray(value)) {
    const messages = value.filter(
      (item): item is string =>
        typeof item === "string" && Boolean(item.trim()),
    );
    return messages.length > 0 ? messages.join(" ") : null;
  }

  return null;
}

export function parseApiFieldErrors<Field extends string>(
  error: unknown,
  fields: readonly Field[],
): FieldErrors<Field> {
  const fieldErrors: FieldErrors<Field> = {};

  if (!(error instanceof ApiError)) {
    return fieldErrors;
  }

  const data = error.data;
  if (!isRecord(data)) {
    return fieldErrors;
  }

  fields.forEach((field) => {
    const message = getErrorText(data[field]);
    if (message) {
      fieldErrors[field] = message;
    }
  });

  return fieldErrors;
}

export function hasFieldErrors<Field extends string>(
  fieldErrors: FieldErrors<Field>,
): boolean {
  return Object.values(fieldErrors).some(Boolean);
}

export function isApiErrorStatus(error: unknown, status: number): boolean {
  return error instanceof ApiError && error.status === status;
}
