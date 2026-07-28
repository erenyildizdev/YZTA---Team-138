import { AlertCircle, CheckCircle, RefreshCw, Sparkles } from "lucide-react";

export type AnalysisStepStatus = "pending" | "active" | "completed" | "error";

export interface AnalysisStep {
  id: string;
  label: string;
  status: AnalysisStepStatus;
}

interface IdeaAnalysisProgressProps {
  steps: AnalysisStep[];
  error?: string | null;
  onRetry?: () => void;
  isRunning: boolean;
}

export function IdeaAnalysisProgress({
  steps,
  error,
  onRetry,
  isRunning,
}: IdeaAnalysisProgressProps) {
  return (
    <div
      className="flex flex-1 items-center justify-center overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
      aria-busy={isRunning}
    >
      <div className="w-full max-w-sm px-6 py-10 text-center">
        <div className="mx-auto mb-7 flex h-16 w-16 items-center justify-center rounded-2xl border border-primary/20 bg-primary/15">
          <Sparkles
            size={26}
            className={isRunning ? "animate-pulse text-primary" : "text-primary"}
            aria-hidden="true"
          />
        </div>

        <div role="status" aria-live="polite" aria-atomic="true">
          <h1 className="text-xl font-bold text-foreground">
            {isRunning ? "Doğrulama akışı çalışıyor" : "Analiz tamamlanamadı"}
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            {isRunning
              ? "Analiz adımları sunucuda sırasıyla çalıştırılıyor. Sonuçlar hazır olduğunda analiz ekranına yönlendirileceksin."
              : "Fikir kaydın korunuyor. Akışı aynı fikir için yeniden deneyebilirsin."}
          </p>
        </div>

        <div className="mt-8 space-y-3 text-left">
          {steps.map((step) => (
            <div
              key={step.id}
              className="flex min-w-0 items-start gap-3 transition-opacity"
            >
              <div
                className={`mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full ${
                  step.status === "completed"
                    ? "bg-success"
                    : step.status === "active"
                      ? "bg-primary"
                      : step.status === "error"
                        ? "bg-destructive"
                        : "bg-border"
                }`}
                aria-hidden="true"
              >
                {step.status === "completed" && (
                  <CheckCircle size={11} className="text-primary-foreground" />
                )}
                {step.status === "active" && (
                  <span className="h-2 w-2 animate-pulse rounded-full bg-primary-foreground" />
                )}
                {step.status === "error" && (
                  <AlertCircle size={11} className="text-destructive-foreground" />
                )}
              </div>
              <div className="flex min-w-0 flex-1 flex-col gap-0.5 sm:flex-row sm:items-center sm:justify-between sm:gap-3">
                <span
                  className={`min-w-0 break-words text-sm ${
                    step.status === "pending"
                      ? "text-muted-foreground"
                      : "font-medium text-foreground"
                  }`}
                >
                  {step.label}
                </span>
                <span
                  className={`flex-shrink-0 text-[11px] font-medium ${
                    step.status === "error"
                      ? "text-destructive"
                      : step.status === "active"
                        ? "text-primary"
                        : "text-muted-foreground"
                  }`}
                >
                  {step.status === "completed"
                    ? "Tamamlandı"
                    : step.status === "active"
                      ? "Çalışıyor"
                      : step.status === "error"
                        ? "Başarısız"
                        : "Bekliyor"}
                </span>
              </div>
            </div>
          ))}
        </div>

        {error && (
          <div
            className="mt-7 min-w-0 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-left"
            role="alert"
            aria-live="assertive"
            aria-atomic="true"
          >
            <p className="break-words text-sm text-destructive">
              {isRunning ? `Önceki deneme: ${error}` : error}
            </p>
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                disabled={isRunning}
                aria-disabled={isRunning}
                className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground transition-colors hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-primary sm:w-auto"
              >
                <RefreshCw size={12} aria-hidden="true" />
                {isRunning ? "Yeniden deneniyor..." : "Yeniden dene"}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
