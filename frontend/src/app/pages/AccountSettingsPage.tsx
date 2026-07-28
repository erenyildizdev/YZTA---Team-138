import { type FormEvent, useState } from "react";
import { CheckCircle2, KeyRound, User } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { ApiError, changePassword, updateProfile } from "../lib/api";

export function AccountSettingsPage() {
  const { user, updateUser } = useAuth();

  const [firstName, setFirstName] = useState(user?.first_name ?? "");
  const [lastName, setLastName] = useState(user?.last_name ?? "");
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [isSavingPassword, setIsSavingPassword] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const handleProfileSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (isSavingProfile) return;

    setProfileError(null);
    setProfileSuccess(false);
    setIsSavingProfile(true);

    try {
      const updated = await updateProfile({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
      });
      updateUser(updated);
      setProfileSuccess(true);
    } catch (err) {
      setProfileError(err instanceof ApiError ? err.message : "Profil güncellenemedi.");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handlePasswordSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (isSavingPassword) return;

    setPasswordError(null);
    setPasswordSuccess(false);

    if (newPassword.length < 8) {
      setPasswordError("Yeni şifre en az 8 karakter olmalı.");
      return;
    }
    if (newPassword !== newPasswordConfirm) {
      setPasswordError("Yeni şifreler eşleşmiyor.");
      return;
    }

    setIsSavingPassword(true);
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
      setNewPasswordConfirm("");
    } catch (err) {
      setPasswordError(err instanceof ApiError ? err.message : "Şifre güncellenemedi.");
    } finally {
      setIsSavingPassword(false);
    }
  };

  return (
    <div
      className="hide-scroll flex-1 overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="mx-auto max-w-2xl px-4 py-7 sm:px-7 sm:py-10">
        <div className="mb-7">
          <h1 className="text-xl font-bold text-foreground">Hesap Ayarları</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Profil bilgilerini görüntüle, güncelle ve şifreni değiştir.
          </p>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="mb-4 flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-muted">
                <User size={14} className="text-foreground" />
              </div>
              <h2 className="text-sm font-semibold text-foreground">Profil Bilgileri</h2>
            </div>

            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">E-posta</label>
                <input
                  type="email"
                  value={user?.email ?? ""}
                  disabled
                  className="w-full cursor-not-allowed rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-muted-foreground"
                />
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Ad</label>
                  <input
                    type="text"
                    required
                    value={firstName}
                    onChange={(e) => {
                      setFirstName(e.target.value);
                      setProfileSuccess(false);
                    }}
                    className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Soyad</label>
                  <input
                    type="text"
                    required
                    value={lastName}
                    onChange={(e) => {
                      setLastName(e.target.value);
                      setProfileSuccess(false);
                    }}
                    className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                  />
                </div>
              </div>

              {profileError && (
                <p className="text-xs text-destructive">{profileError}</p>
              )}

              {profileSuccess && (
                <p className="flex items-center gap-1.5 text-xs text-success">
                  <CheckCircle2 size={13} />
                  Profil güncellendi.
                </p>
              )}

              <button
                type="submit"
                disabled={isSavingProfile}
                className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-all hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSavingProfile ? "Kaydediliyor..." : "Kaydet"}
              </button>
            </form>
          </div>

          <div className="rounded-xl border border-border bg-card p-5">
            <div className="mb-4 flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-muted">
                <KeyRound size={14} className="text-foreground" />
              </div>
              <h2 className="text-sm font-semibold text-foreground">Şifre Değiştir</h2>
            </div>

            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Mevcut Şifre</label>
                <input
                  type="password"
                  required
                  value={currentPassword}
                  onChange={(e) => {
                    setCurrentPassword(e.target.value);
                    setPasswordSuccess(false);
                  }}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                />
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Yeni Şifre</label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => {
                      setNewPassword(e.target.value);
                      setPasswordSuccess(false);
                    }}
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Yeni Şifre (Tekrar)</label>
                  <input
                    type="password"
                    required
                    value={newPasswordConfirm}
                    onChange={(e) => {
                      setNewPasswordConfirm(e.target.value);
                      setPasswordSuccess(false);
                    }}
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                  />
                </div>
              </div>

              {passwordError && (
                <p className="text-xs text-destructive">{passwordError}</p>
              )}

              {passwordSuccess && (
                <p className="flex items-center gap-1.5 text-xs text-success">
                  <CheckCircle2 size={13} />
                  Şifre güncellendi.
                </p>
              )}

              <button
                type="submit"
                disabled={isSavingPassword}
                className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-all hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSavingPassword ? "Kaydediliyor..." : "Şifreyi Güncelle"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
