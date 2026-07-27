import { type KeyboardEvent, useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  FileText,
  Lightbulb,
  Sparkles,
  Target,
  Users,
} from "lucide-react";
import { ApiError, createIdea } from "../lib/api";
import { useActiveIdeaId } from "../hooks/useActiveIdeaId";

const SECTORS = [
  "SaaS / Prodüktivite",
  "F&B Teknolojisi",
  "EdTech",
  "FinTech",
  "Sağlık Teknolojisi (HealthTech)",
  "E-ticaret",
  "Mobilite / Ulaşım",
  "Oyun",
  "Sürdürülebilirlik",
  "Diğer",
];

const TARGET_AUDIENCES = [
  "Restoran sahipleri",
  "Freelancer'lar",
  "Üniversite öğrencileri",
  "KOBİ'ler",
  "Bireysel tüketiciler",
  "Kurumsal şirketler",
  "Girişimciler",
  "Ebeveynler",
  "Sağlık çalışanları",
  "Diğer",
];

const OTHER_OPTION = "Diğer";
const MIN_LENGTH = 10;

type FieldKey = "title" | "sector" | "target_audience" | "description" | "problem" | "solution";

interface StepConfig {
  key: FieldKey;
  label: string;
  icon: typeof Lightbulb;
  type: "text" | "select" | "textarea";
  placeholder: string;
  helper: string;
  options?: string[];
  otherPlaceholder?: string;
}

const STEPS: StepConfig[] = [
  {
    key: "title",
    label: "Fikir Başlığı",
    icon: Lightbulb,
    type: "text",
    placeholder: "Örn. Restoran Stok Yönetim Uygulaması",
    helper: "Fikrini kısa ve akılda kalıcı bir başlıkla özetle.",
  },
  {
    key: "sector",
    label: "Sektör / Kategori",
    icon: Sparkles,
    type: "select",
    placeholder: "Seçiniz",
    helper: "Fikrin hangi alana en yakın?",
    options: SECTORS,
    otherPlaceholder: "Sektörünü yaz...",
  },
  {
    key: "target_audience",
    label: "Hedef Kitle",
    icon: Users,
    type: "select",
    placeholder: "Seçiniz",
    helper: "Bu ürünü asıl kim kullanacak?",
    options: TARGET_AUDIENCES,
    otherPlaceholder: "Hedef kitleni yaz...",
  },
  {
    key: "description",
    label: "İş Fikri Açıklaması",
    icon: FileText,
    type: "textarea",
    placeholder: "Fikrini kısaca özetle...",
    helper: "Fikrini birkaç cümleyle anlat.",
  },
  {
    key: "problem",
    label: "Problem",
    icon: AlertTriangle,
    type: "textarea",
    placeholder: "Hedef kitlenin yaşadığı problem ne?",
    helper: "Çözmeye çalıştığın sorunu tanımla.",
  },
  {
    key: "solution",
    label: "Çözüm Önerisi",
    icon: Target,
    type: "textarea",
    placeholder: "Bu problemi nasıl çözüyorsun?",
    helper: "Önerdiğin çözümü açıkla.",
  },
];

const initialValues: Record<FieldKey, string> = {
  title: "",
  sector: "",
  target_audience: "",
  description: "",
  problem: "",
  solution: "",
};

export function NewIdeaPage({ onCreated }: { onCreated: () => void }) {
  const [, setIdeaId] = useActiveIdeaId();

  const [stepIndex, setStepIndex] = useState(0);
  const [values, setValues] = useState<Record<FieldKey, string>>(initialValues);
  const [otherMode, setOtherMode] = useState<Partial<Record<FieldKey, boolean>>>({});
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<FieldKey, string>>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const step = STEPS[stepIndex];
  const isLastStep = stepIndex === STEPS.length - 1;

  const setValue = (key: FieldKey, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    if (fieldErrors[key]) setFieldErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const validateStep = (key: FieldKey) => {
    const config = STEPS.find((s) => s.key === key)!;
    const value = values[key].trim();
    let error: string | undefined;

    if (!value) {
      error = `${config.label} boş bırakılamaz.`;
    } else if (config.type === "textarea" && value.length < MIN_LENGTH) {
      error = `${config.label} en az ${MIN_LENGTH} karakter olmalı.`;
    }

    setFieldErrors((prev) => ({ ...prev, [key]: error }));
    return !error;
  };

  const handleBack = () => {
    if (stepIndex === 0) return;
    setFormError(null);
    setStepIndex((i) => i - 1);
  };

  const handleNext = async () => {
    if (!validateStep(step.key)) return;

    if (!isLastStep) {
      setStepIndex((i) => i + 1);
      return;
    }

    setFormError(null);
    setIsSubmitting(true);
    try {
      const idea = await createIdea({
        title: values.title.trim(),
        description: values.description.trim(),
        target_audience: values.target_audience.trim(),
        problem: values.problem.trim(),
        solution: values.solution.trim(),
        sector: values.sector,
      });
      setIdeaId(idea.id);
      onCreated();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Fikir kaydedilemedi. Lütfen tekrar dene.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTextKeyDown = (event: KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleNext();
    }
  };

  const error = fieldErrors[step.key];
  const inputClass = `w-full bg-muted border rounded-xl px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 transition-all ${
    error
      ? "border-destructive/50 focus:border-destructive focus:ring-destructive/30"
      : "border-border focus:border-primary/50 focus:ring-primary/20"
  }`;

  return (
    <div className="flex-1 overflow-y-auto hide-scroll" style={{ animation: "page-in 0.3s ease-out" }}>
      <div className="max-w-xl mx-auto px-4 sm:px-7 py-7 sm:py-10">
        <div className="flex items-center gap-2.5 mb-2">
          <span className="w-9 h-9 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
            <Lightbulb size={16} className="text-primary" />
          </span>
          <h1 className="text-xl font-bold text-foreground">Yeni Fikir Ekle</h1>
        </div>
        <p className="text-sm text-muted-foreground mb-6">
          Sorulara sırayla cevap ver, kaydettikten sonra seni doğrudan analiz ekranına yönlendirelim.
        </p>

        {/* Progress */}
        <div className="flex items-center gap-1.5 mb-7">
          {STEPS.map((s, i) => (
            <div
              key={s.key}
              className={`h-1.5 flex-1 rounded-full transition-all ${
                i < stepIndex ? "bg-primary" : i === stepIndex ? "bg-primary/60" : "bg-secondary"
              }`}
            />
          ))}
        </div>

        <div className="bg-card border border-border rounded-2xl p-6" style={{ minHeight: 280 }}>
          <div key={step.key} style={{ animation: "step-appear 0.35s ease-out" }}>
            <span className="text-[11px] font-semibold text-primary uppercase tracking-widest">
              Adım {stepIndex + 1} / {STEPS.length}
            </span>

            <div className="flex items-center gap-2 mt-2 mb-1.5">
              <step.icon size={15} className="text-muted-foreground" />
              <h2 className="text-base font-bold text-foreground">{step.label}</h2>
            </div>
            <p className="text-xs text-muted-foreground mb-4">{step.helper}</p>

            {step.type === "text" && (
              <input
                autoFocus
                type="text"
                value={values[step.key]}
                onChange={(e) => setValue(step.key, e.target.value)}
                onKeyDown={handleTextKeyDown}
                placeholder={step.placeholder}
                className={inputClass}
              />
            )}

            {step.type === "select" && (
              <>
                <select
                  autoFocus={!otherMode[step.key]}
                  value={otherMode[step.key] ? OTHER_OPTION : values[step.key]}
                  onChange={(e) => {
                    const selected = e.target.value;
                    if (selected === OTHER_OPTION) {
                      setOtherMode((prev) => ({ ...prev, [step.key]: true }));
                      setValue(step.key, "");
                    } else {
                      setOtherMode((prev) => ({ ...prev, [step.key]: false }));
                      setValue(step.key, selected);
                    }
                  }}
                  className={inputClass}
                >
                  <option value="" disabled>
                    {step.placeholder}
                  </option>
                  {step.options!.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>

                {otherMode[step.key] && (
                  <input
                    autoFocus
                    type="text"
                    value={values[step.key]}
                    onChange={(e) => setValue(step.key, e.target.value)}
                    onKeyDown={handleTextKeyDown}
                    placeholder={step.otherPlaceholder}
                    className={`${inputClass} mt-2.5`}
                  />
                )}
              </>
            )}

            {step.type === "textarea" && (
              <textarea
                autoFocus
                value={values[step.key]}
                onChange={(e) => setValue(step.key, e.target.value)}
                rows={4}
                placeholder={step.placeholder}
                className={`${inputClass} resize-none`}
              />
            )}

            {error && <p className="text-xs text-destructive mt-1.5">{error}</p>}

            {isLastStep && formError && (
              <div className="flex items-start gap-2 bg-destructive/10 border border-destructive/30 rounded-xl px-3 py-2.5 mt-4">
                <AlertTriangle size={13} className="text-destructive mt-0.5 flex-shrink-0" />
                <p className="text-xs text-destructive leading-relaxed">{formError}</p>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between mt-6">
            <button
              type="button"
              onClick={handleBack}
              disabled={stepIndex === 0}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-hover transition-all disabled:opacity-0 disabled:pointer-events-none"
            >
              <ArrowLeft size={13} />Geri
            </button>

            <button
              type="button"
              onClick={handleNext}
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl px-5 py-2.5 text-sm font-semibold transition-all disabled:opacity-50"
            >
              {isSubmitting ? "Kaydediliyor..." : isLastStep ? "Kaydet ve Analize Geç" : "İleri"}
              {!isSubmitting && <ArrowRight size={14} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
