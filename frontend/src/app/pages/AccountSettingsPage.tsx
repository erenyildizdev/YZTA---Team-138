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
  User,
} from "lucide-react";
import { useNavigate } from "react-router";

import { PasswordInput } from "../components/auth/PasswordInput";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Skeleton } from "../components/ui/skeleton";
import { useAuth } from "../context/AuthContext";
import {
  ApiError,
  changeCurrentUserPassword,
  getAccessToken,
  getCurrentUserProfile,
  updateCurrentUserProfile,
  type UpdateAccountProfilePayload,
} from "../lib/api";

const REAUTH_MESSAGE_KEY = "password_change_message";
const REAUTH_MESSAGE =
  "Parolanız güncellendi. Yeni parolanızla giriş yapın.";
const PROFILE_FIELD_MAX_LENGTH = 150;

type ProfileField = "first_name" | "last_name";
type PasswordField =
  | "current_password"
  | "new_password"
  | "new_password_confirm";

type FieldErrors<Field extends string> = Partial<
  Record<Field, string>
>;

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

function parseFormError<Field extends string>(
  error: unknown,
  fields: readonly Field[],
  fallbackMessage: string,
): {
  fieldErrors: FieldErrors<Field>;
  generalError: string | null;
} {
  const fieldErrors: FieldErrors<Field> = {};

  if (!(error instanceof ApiError)) {
    return {
      fieldErrors,
      generalError: fallbackMessage,
    };
  }

  if (isRecord(error.data)) {
    fields.forEach((field) => {
      const message = getErrorText(error.data?.[field]);
      if (message) {
        fieldErrors[field] = message;
      }
    });

    const generalError =
      getErrorText(error.data.detail) ??
      getErrorText(error.data.message) ??
      getErrorText(error.data.non_field_errors);

    if (generalError) {
      return { fieldErrors, generalError };
    }
  }

  return {
    fieldErrors,
    generalError:
      Object.keys(fieldErrors).length > 0
        ? null
        : error.message || fallbackMessage,
  };
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

function describedBy(
  ...ids: Array<string | null | false | undefined>
): string | undefined {
  const validIds = ids.filter((id): id is string => Boolean(id));
  return validIds.length > 0 ? validIds.join(" ") : undefined;
}

export function AccountSettingsPage() {
  const { logout, updateUser } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [isProfileReady, setIsProfileReady] = useState(false);
  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileLoadError, setProfileLoadError] = useState<string | null>(
    null,
  );
  const [profileFieldErrors, setProfileFieldErrors] = useState<
    FieldErrors<ProfileField>
  >({});
  const [profileGeneralError, setProfileGeneralError] = useState<
    string | null
  >(null);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(
    null,
  );

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [isSavingPassword, setIsSavingPassword] = useState(false);
  const [passwordFieldErrors, setPasswordFieldErrors] = useState<
    FieldErrors<PasswordField>
  >({});
  const [passwordGeneralError, setPasswordGeneralError] = useState<
    string | null
  >(null);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(
    null,
  );

  const mountedRef = useRef(false);
  const sessionEndingRef = useRef(false);
  const profileLoadGenerationRef = useRef(0);
  const profileLoadAbortRef = useRef<AbortController | null>(null);
  const profileSubmitInFlightRef = useRef(false);
  const passwordSubmitInFlightRef = useRef(false);
  const savedProfileRef = useRef({
    firstName: "",
    lastName: "",
  });

  const loadProfile = async () => {
    const generation = profileLoadGenerationRef.current + 1;
    profileLoadGenerationRef.current = generation;
    profileLoadAbortRef.current?.abort();

    const controller = new AbortController();
    const requestToken = getAccessToken();
    profileLoadAbortRef.current = controller;

    if (mountedRef.current) {
      setIsProfileLoading(true);
      setProfileLoadError(null);
      setProfileGeneralError(null);
      setProfileSuccess(null);
    }

    try {
      const profile = await getCurrentUserProfile(controller.signal);

      if (
        !mountedRef.current ||
        sessionEndingRef.current ||
        generation !== profileLoadGenerationRef.current ||
        getAccessToken() !== requestToken
      ) {
        return;
      }

      savedProfileRef.current = {
        firstName: profile.first_name,
        lastName: profile.last_name,
      };
      setEmail(profile.email);
      setFirstName(profile.first_name);
      setLastName(profile.last_name);
      setProfileFieldErrors({});
      setIsProfileReady(true);
      updateUser(profile);
    } catch (error) {
      if (
        isAbortError(error) ||
        !mountedRef.current ||
        sessionEndingRef.current ||
        generation !== profileLoadGenerationRef.current ||
        getAccessToken() !== requestToken
      ) {
        return;
      }

      setIsProfileReady(false);
      setProfileLoadError(
        error instanceof ApiError
          ? error.message
          : "Profil bilgileri yüklenemedi.",
      );
    } finally {
      if (profileLoadAbortRef.current === controller) {
        profileLoadAbortRef.current = null;
      }

      if (
        mountedRef.current &&
        generation === profileLoadGenerationRef.current &&
        !sessionEndingRef.current
      ) {
        setIsProfileLoading(false);
      }
    }
  };

  useEffect(() => {
    mountedRef.current = true;
    void loadProfile();

    return () => {
      mountedRef.current = false;
      profileLoadGenerationRef.current += 1;
      profileLoadAbortRef.current?.abort();
    };
  }, []);

  const normalizedFirstName = firstName.trim();
  const normalizedLastName = lastName.trim();
  const hasFirstNameChange =
    normalizedFirstName !== savedProfileRef.current.firstName;
  const hasLastNameChange =
    normalizedLastName !== savedProfileRef.current.lastName;
  const hasProfileChanges =
    hasFirstNameChange || hasLastNameChange;

  const clearProfileFieldError = (field: ProfileField) => {
    setProfileFieldErrors((current) => ({
      ...current,
      [field]: undefined,
    }));
    setProfileGeneralError(null);
    setProfileSuccess(null);
  };

  const handleProfileSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (
      profileSubmitInFlightRef.current ||
      isProfileLoading ||
      !isProfileReady ||
      sessionEndingRef.current
    ) {
      return;
    }

    setProfileFieldErrors({});
    setProfileGeneralError(null);
    setProfileSuccess(null);

    const clientErrors: FieldErrors<ProfileField> = {};
    if (hasFirstNameChange && !normalizedFirstName) {
      clientErrors.first_name = "Ad alanı boş bırakılamaz.";
    } else if (
      hasFirstNameChange &&
      normalizedFirstName.length > PROFILE_FIELD_MAX_LENGTH
    ) {
      clientErrors.first_name = `Ad en fazla ${PROFILE_FIELD_MAX_LENGTH} karakter olabilir.`;
    }

    if (hasLastNameChange && !normalizedLastName) {
      clientErrors.last_name = "Soyad alanı boş bırakılamaz.";
    } else if (
      hasLastNameChange &&
      normalizedLastName.length > PROFILE_FIELD_MAX_LENGTH
    ) {
      clientErrors.last_name = `Soyad en fazla ${PROFILE_FIELD_MAX_LENGTH} karakter olabilir.`;
    }

    if (Object.keys(clientErrors).length > 0) {
      setProfileFieldErrors(clientErrors);
      return;
    }

    const payload: UpdateAccountProfilePayload = {};
    if (hasFirstNameChange) {
      payload.first_name = normalizedFirstName;
    }
    if (hasLastNameChange) {
      payload.last_name = normalizedLastName;
    }

    if (Object.keys(payload).length === 0) {
      setProfileSuccess("Kaydedilecek bir değişiklik yok.");
      return;
    }

    profileSubmitInFlightRef.current = true;
    setIsSavingProfile(true);

    profileLoadGenerationRef.current += 1;
    profileLoadAbortRef.current?.abort();
    const requestToken = getAccessToken();

    try {
      const updatedProfile =
        await updateCurrentUserProfile(payload);

      if (
        !mountedRef.current ||
        sessionEndingRef.current ||
        getAccessToken() !== requestToken
      ) {
        return;
      }

      savedProfileRef.current = {
        firstName: updatedProfile.first_name,
        lastName: updatedProfile.last_name,
      };
      setEmail(updatedProfile.email);
      setFirstName(updatedProfile.first_name);
      setLastName(updatedProfile.last_name);
      setProfileFieldErrors({});
      setProfileSuccess("Profil bilgileri güncellendi.");
      updateUser(updatedProfile);
    } catch (error) {
      if (
        !mountedRef.current ||
        sessionEndingRef.current ||
        getAccessToken() !== requestToken
      ) {
        return;
      }

      const parsedError = parseFormError(
        error,
        ["first_name", "last_name"] as const,
        "Profil bilgileri güncellenemedi.",
      );
      setProfileFieldErrors(parsedError.fieldErrors);
      setProfileGeneralError(parsedError.generalError);
    } finally {
      profileSubmitInFlightRef.current = false;
      if (mountedRef.current && !sessionEndingRef.current) {
        setIsSavingProfile(false);
      }
    }
  };

  const clearPasswordFieldErrors = (...fields: PasswordField[]) => {
    setPasswordFieldErrors((current) => {
      const nextErrors = { ...current };
      fields.forEach((field) => {
        nextErrors[field] = undefined;
      });
      return nextErrors;
    });
    setPasswordGeneralError(null);
    setPasswordSuccess(null);
  };

  const handlePasswordSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (
      passwordSubmitInFlightRef.current ||
      sessionEndingRef.current
    ) {
      return;
    }

    setPasswordFieldErrors({});
    setPasswordGeneralError(null);
    setPasswordSuccess(null);

    const clientErrors: FieldErrors<PasswordField> = {};
    if (!currentPassword) {
      clientErrors.current_password = "Mevcut parola gereklidir.";
    }
    if (!newPassword) {
      clientErrors.new_password = "Yeni parola gereklidir.";
    }
    if (!newPasswordConfirm) {
      clientErrors.new_password_confirm =
        "Yeni parola tekrarı gereklidir.";
    }
    if (
      newPassword &&
      newPasswordConfirm &&
      newPassword !== newPasswordConfirm
    ) {
      clientErrors.new_password_confirm =
        "Yeni parolalar eşleşmiyor.";
    }
    if (
      currentPassword &&
      newPassword &&
      currentPassword === newPassword
    ) {
      clientErrors.new_password =
        "Yeni parola mevcut paroladan farklı olmalıdır.";
    }

    if (Object.keys(clientErrors).length > 0) {
      setPasswordFieldErrors(clientErrors);
      return;
    }

    passwordSubmitInFlightRef.current = true;
    setIsSavingPassword(true);
    const requestToken = getAccessToken();

    try {
      const response = await changeCurrentUserPassword({
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      });

      if (
        sessionEndingRef.current ||
        getAccessToken() !== requestToken
      ) {
        return;
      }

      if (response.requires_reauthentication) {
        sessionEndingRef.current = true;
        profileLoadGenerationRef.current += 1;
        profileLoadAbortRef.current?.abort();

        try {
          sessionStorage.setItem(REAUTH_MESSAGE_KEY, REAUTH_MESSAGE);
        } catch {
          // Router state below still carries the one-time message.
        }

        logout();

        if (mountedRef.current) {
          navigate("/login", {
            replace: true,
            state: { passwordChangeMessage: REAUTH_MESSAGE },
          });
        }
        return;
      }

      if (!mountedRef.current) {
        return;
      }

      setCurrentPassword("");
      setNewPassword("");
      setNewPasswordConfirm("");
      setPasswordSuccess(
        response.detail || "Parolanız başarıyla güncellendi.",
      );
    } catch (error) {
      if (
        !mountedRef.current ||
        sessionEndingRef.current ||
        getAccessToken() !== requestToken
      ) {
        return;
      }

      const parsedError = parseFormError(
        error,
        [
          "current_password",
          "new_password",
          "new_password_confirm",
        ] as const,
        "Parola güncellenemedi.",
      );
      setPasswordFieldErrors(parsedError.fieldErrors);
      setPasswordGeneralError(parsedError.generalError);
    } finally {
      passwordSubmitInFlightRef.current = false;
      if (mountedRef.current && !sessionEndingRef.current) {
        setIsSavingPassword(false);
      }
    }
  };

  return (
    <div className="hide-scroll flex-1 overflow-y-auto">
      <div className="mx-auto max-w-2xl px-4 py-7 sm:px-7 sm:py-10">
        <div className="mb-7">
          <h1 className="text-xl font-bold text-foreground">
            Hesap Ayarları
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Profil bilgilerini görüntüle, güncelle ve parolanı değiştir.
          </p>
        </div>

        <div className="space-y-6">
          <Card
            aria-labelledby="profile-settings-title"
            className="gap-0 p-5"
          >
            <div className="mb-4 flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-muted">
                <User aria-hidden="true" size={14} className="text-foreground" />
              </div>
              <h2
                id="profile-settings-title"
                className="text-sm font-semibold text-foreground"
              >
                Profil Bilgileri
              </h2>
            </div>

            {isProfileLoading && (
              <div
                role="status"
                aria-live="polite"
                aria-label="Profil bilgileri yükleniyor"
                className="space-y-4"
              >
                <Skeleton className="h-16 w-full rounded-xl" />
                <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
                  <Skeleton className="h-16 w-full rounded-xl" />
                  <Skeleton className="h-16 w-full rounded-xl" />
                </div>
                <Skeleton className="h-10 w-full rounded-xl sm:w-28" />
              </div>
            )}

            {!isProfileLoading && profileLoadError && (
              <div className="space-y-3">
                <div
                  role="alert"
                  className="flex min-w-0 items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-3 py-2.5"
                >
                  <AlertTriangle
                    aria-hidden="true"
                    size={14}
                    className="mt-0.5 shrink-0 text-destructive"
                  />
                  <p className="min-w-0 break-words text-xs leading-relaxed text-destructive">
                    {profileLoadError}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => void loadProfile()}
                  className="w-full rounded-xl sm:w-auto"
                >
                  Tekrar Dene
                </Button>
              </div>
            )}

            {!isProfileLoading && isProfileReady && (
              <form
                noValidate
                onSubmit={handleProfileSubmit}
                aria-busy={isSavingProfile}
                className="space-y-4"
              >
                <div className="space-y-1.5">
                  <label
                    htmlFor="account-email"
                    className="block text-xs font-semibold text-muted-foreground"
                  >
                    E-posta
                  </label>
                  <Input
                    id="account-email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    readOnly
                    value={email}
                    aria-describedby="account-email-help"
                    className="h-auto cursor-default rounded-xl border-border bg-muted px-3.5 py-2.5 text-sm text-muted-foreground focus-visible:border-ring focus-visible:ring-2 dark:bg-muted"
                  />
                  <p
                    id="account-email-help"
                    className="text-xs leading-relaxed text-muted-foreground"
                  >
                    E-posta adresi bu ekrandan değiştirilemez.
                  </p>
                </div>

                <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
                  <div className="min-w-0 space-y-1.5">
                    <label
                      htmlFor="account-first-name"
                      className="block text-xs font-semibold text-muted-foreground"
                    >
                      Ad
                    </label>
                    <Input
                      id="account-first-name"
                      name="first_name"
                      type="text"
                      autoComplete="given-name"
                      required
                      maxLength={PROFILE_FIELD_MAX_LENGTH}
                      disabled={isSavingProfile}
                      value={firstName}
                      onChange={(event) => {
                        setFirstName(event.target.value);
                        clearProfileFieldError("first_name");
                      }}
                      aria-invalid={Boolean(
                        profileFieldErrors.first_name,
                      )}
                      aria-describedby={describedBy(
                        profileFieldErrors.first_name &&
                          "account-first-name-error",
                      )}
                      className="h-auto rounded-xl border-border bg-muted px-3.5 py-2.5 text-sm text-foreground focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/20 dark:bg-muted"
                    />
                    {profileFieldErrors.first_name && (
                      <p
                        id="account-first-name-error"
                        role="alert"
                        className="break-words text-xs leading-relaxed text-destructive"
                      >
                        {profileFieldErrors.first_name}
                      </p>
                    )}
                  </div>

                  <div className="min-w-0 space-y-1.5">
                    <label
                      htmlFor="account-last-name"
                      className="block text-xs font-semibold text-muted-foreground"
                    >
                      Soyad
                    </label>
                    <Input
                      id="account-last-name"
                      name="last_name"
                      type="text"
                      autoComplete="family-name"
                      required
                      maxLength={PROFILE_FIELD_MAX_LENGTH}
                      disabled={isSavingProfile}
                      value={lastName}
                      onChange={(event) => {
                        setLastName(event.target.value);
                        clearProfileFieldError("last_name");
                      }}
                      aria-invalid={Boolean(
                        profileFieldErrors.last_name,
                      )}
                      aria-describedby={describedBy(
                        profileFieldErrors.last_name &&
                          "account-last-name-error",
                      )}
                      className="h-auto rounded-xl border-border bg-muted px-3.5 py-2.5 text-sm text-foreground focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/20 dark:bg-muted"
                    />
                    {profileFieldErrors.last_name && (
                      <p
                        id="account-last-name-error"
                        role="alert"
                        className="break-words text-xs leading-relaxed text-destructive"
                      >
                        {profileFieldErrors.last_name}
                      </p>
                    )}
                  </div>
                </div>

                {profileGeneralError && (
                  <p
                    role="alert"
                    className="break-words text-xs leading-relaxed text-destructive"
                  >
                    {profileGeneralError}
                  </p>
                )}

                {profileSuccess && (
                  <p
                    role="status"
                    aria-live="polite"
                    className="flex items-center gap-1.5 text-xs text-success"
                  >
                    <CheckCircle2 aria-hidden="true" size={13} />
                    {profileSuccess}
                  </p>
                )}

                <Button
                  type="submit"
                  disabled={
                    isSavingProfile || !hasProfileChanges
                  }
                  className="w-full rounded-xl bg-primary text-primary-foreground hover:bg-primary-hover sm:w-auto"
                >
                  {isSavingProfile ? "Kaydediliyor..." : "Kaydet"}
                </Button>
              </form>
            )}
          </Card>

          <Card
            aria-labelledby="password-settings-title"
            className="gap-0 p-5"
          >
            <div className="mb-4 flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-muted">
                <KeyRound
                  aria-hidden="true"
                  size={14}
                  className="text-foreground"
                />
              </div>
              <h2
                id="password-settings-title"
                className="text-sm font-semibold text-foreground"
              >
                Parola Değiştir
              </h2>
            </div>

            <form
              noValidate
              onSubmit={handlePasswordSubmit}
              aria-busy={isSavingPassword}
              className="space-y-4"
            >
              <div className="min-w-0 space-y-1.5">
                <label
                  htmlFor="account-current-password"
                  className="block text-xs font-semibold text-muted-foreground"
                >
                  Mevcut Parola
                </label>
                <PasswordInput
                  id="account-current-password"
                  name="current_password"
                  autoComplete="current-password"
                  required
                  disabled={isSavingPassword}
                  value={currentPassword}
                  onChange={(event) => {
                    setCurrentPassword(event.target.value);
                    clearPasswordFieldErrors(
                      "current_password",
                      "new_password",
                    );
                  }}
                  placeholder="••••••••"
                  aria-invalid={Boolean(
                    passwordFieldErrors.current_password,
                  )}
                  aria-describedby={describedBy(
                    passwordFieldErrors.current_password &&
                      "account-current-password-error",
                  )}
                />
                {passwordFieldErrors.current_password && (
                  <p
                    id="account-current-password-error"
                    role="alert"
                    className="break-words text-xs leading-relaxed text-destructive"
                  >
                    {passwordFieldErrors.current_password}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
                <div className="min-w-0 space-y-1.5">
                  <label
                    htmlFor="account-new-password"
                    className="block text-xs font-semibold text-muted-foreground"
                  >
                    Yeni Parola
                  </label>
                  <PasswordInput
                    id="account-new-password"
                    name="new_password"
                    autoComplete="new-password"
                    required
                    disabled={isSavingPassword}
                    value={newPassword}
                    onChange={(event) => {
                      setNewPassword(event.target.value);
                      clearPasswordFieldErrors(
                        "new_password",
                        "new_password_confirm",
                      );
                    }}
                    placeholder="••••••••"
                    aria-invalid={Boolean(
                      passwordFieldErrors.new_password,
                    )}
                    aria-describedby={describedBy(
                      passwordFieldErrors.new_password &&
                        "account-new-password-error",
                    )}
                  />
                  {passwordFieldErrors.new_password && (
                    <p
                      id="account-new-password-error"
                      role="alert"
                      className="break-words text-xs leading-relaxed text-destructive"
                    >
                      {passwordFieldErrors.new_password}
                    </p>
                  )}
                </div>

                <div className="min-w-0 space-y-1.5">
                  <label
                    htmlFor="account-new-password-confirm"
                    className="block text-xs font-semibold text-muted-foreground"
                  >
                    Yeni Parola (Tekrar)
                  </label>
                  <PasswordInput
                    id="account-new-password-confirm"
                    name="new_password_confirm"
                    autoComplete="new-password"
                    required
                    disabled={isSavingPassword}
                    value={newPasswordConfirm}
                    onChange={(event) => {
                      setNewPasswordConfirm(event.target.value);
                      clearPasswordFieldErrors(
                        "new_password_confirm",
                      );
                    }}
                    placeholder="••••••••"
                    aria-invalid={Boolean(
                      passwordFieldErrors.new_password_confirm,
                    )}
                    aria-describedby={describedBy(
                      passwordFieldErrors.new_password_confirm &&
                        "account-new-password-confirm-error",
                    )}
                  />
                  {passwordFieldErrors.new_password_confirm && (
                    <p
                      id="account-new-password-confirm-error"
                      role="alert"
                      className="break-words text-xs leading-relaxed text-destructive"
                    >
                      {passwordFieldErrors.new_password_confirm}
                    </p>
                  )}
                </div>
              </div>

              {passwordGeneralError && (
                <p
                  role="alert"
                  className="break-words text-xs leading-relaxed text-destructive"
                >
                  {passwordGeneralError}
                </p>
              )}

              {passwordSuccess && (
                <p
                  role="status"
                  aria-live="polite"
                  className="flex items-center gap-1.5 text-xs text-success"
                >
                  <CheckCircle2 aria-hidden="true" size={13} />
                  {passwordSuccess}
                </p>
              )}

              <Button
                type="submit"
                disabled={isSavingPassword}
                className="w-full rounded-xl bg-primary text-primary-foreground hover:bg-primary-hover sm:w-auto"
              >
                {isSavingPassword
                  ? "Güncelleniyor..."
                  : "Parolayı Güncelle"}
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
