import {
  AlertCircle,
  History,
  Lightbulb,
  LoaderCircle,
  Plus,
  RefreshCw,
} from "lucide-react";
import { Link } from "react-router";

import { Button } from "../ui/button";

export type ActiveIdeaPageStateProps = {
  mode: "loading" | "empty" | "error";
  onRetry?: () => void;
};

export function ActiveIdeaPageState({
  mode,
  onRetry,
}: ActiveIdeaPageStateProps) {
  if (mode === "loading") {
    return (
      <div
        className="flex min-h-[18rem] flex-1 items-center justify-center"
        role="status"
        aria-label="Fikir yükleniyor"
      >
        <LoaderCircle className="size-6 animate-spin text-primary" />
        <span className="sr-only">Fikir yükleniyor...</span>
      </div>
    );
  }

  return (
    <div
      className="hide-scroll flex min-h-0 flex-1 overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="mx-auto flex min-h-full w-full max-w-4xl items-center justify-center px-4 py-7 sm:px-7 sm:py-10">
        <section className="w-full max-w-lg rounded-2xl border border-dashed border-border bg-card px-5 py-10 text-center shadow-sm sm:px-10 sm:py-14">
          {mode === "empty" ? (
            <>
              <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
                <Lightbulb size={22} aria-hidden="true" />
              </span>

              <h1 className="mt-4 text-lg font-bold text-foreground">
                Aktif bir fikir bulunamadı
              </h1>

              <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
                Devam etmek için geçmiş fikirlerinden birini seçebilir veya yeni
                bir fikir oluşturabilirsin.
              </p>

              <div className="mt-6 flex flex-col-reverse justify-center gap-2 sm:flex-row">
                <Button asChild variant="outline">
                  <Link to="/history">
                    <History aria-hidden="true" />
                    Geçmiş Fikirler
                  </Link>
                </Button>

                <Button asChild>
                  <Link to="/ideas/new">
                    <Plus aria-hidden="true" />
                    Yeni Fikir Oluştur
                  </Link>
                </Button>
              </div>
            </>
          ) : (
            <>
              <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
                <AlertCircle size={22} aria-hidden="true" />
              </span>

              <h1 className="mt-4 text-lg font-bold text-foreground">
                Fikir yüklenemedi
              </h1>

              <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
                Bir sorun oluştu. Lütfen bağlantını kontrol edip tekrar dene.
              </p>

              <Button className="mt-6" type="button" onClick={onRetry}>
                <RefreshCw aria-hidden="true" />
                Tekrar Dene
              </Button>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
