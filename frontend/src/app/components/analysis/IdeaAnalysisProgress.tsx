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
}

export function IdeaAnalysisProgress({
  steps,
  error,
  onRetry,
}: IdeaAnalysisProgressProps) {
  return (
    <div
      className="flex flex-1 items-center justify-center overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="w-full max-w-sm px-6 py-10 text-center">
        <div className="mx-auto mb-7 flex h-16 w-16 items-center justify-center rounded-2xl border border-primary/20 bg-primary/15">
          <Sparkles size={26} className="animate-pulse text-primary" />
        </div>

        <h1 className="text-xl font-bold text-foreground">Fikrin analiz ediliyor</h1>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
          AI; riskli varsayımları, müşteri sorularını, MVP kapsamını ve doğrulama
          yol haritanı hazırlıyor.
        </p>

        <div className="mt-8 space-y-3 text-left" aria-live="polite">
          {steps.map((step) => (
            <div
              key={step.id}
              className={`flex items-center gap-3 transition-opacity ${
                step.status === "pending" ? "opacity-35" : "opacity-100"
              }`}
            >
              <div
                className={`flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full ${
                  step.status === "completed"
                    ? "bg-success"
                    : step.status === "active"
                      ? "bg-primary"
                      : step.status === "error"
                        ? "bg-destructive"
                        : "bg-border"
                }`}
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
              <span
                className={`text-sm ${
                  step.status === "pending"
                    ? "text-muted-foreground"
                    : "font-medium text-foreground"
                }`}
              >
                {step.label}
              </span>
            </div>
          ))}
        </div>

        {error && (
          <div className="mt-7 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-left">
            <p className="text-sm text-destructive">{error}</p>
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="mt-3 inline-flex items-center gap-2 rounded-lg bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground transition-colors hover:bg-primary-hover"
              >
                <RefreshCw size={12} />
                Yeniden dene
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
