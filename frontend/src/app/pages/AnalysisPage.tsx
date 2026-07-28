import { type FormEvent, useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  ClipboardList,
  FileText,
  Map,
  Megaphone,
  MessageSquare,
  Pencil,
  RefreshCw,
  Send,
  Sparkles,
  Star,
  Tag,
  Target,
  TrendingUp,
  Users,
  XCircle,
} from "lucide-react";

import { CompetitorAnalysisBody } from "../components/analysis/CompetitorAnalysisBody";
import { GeneralEvaluationBody } from "../components/analysis/GeneralEvaluationBody";
import { InterviewNotesBody } from "../components/analysis/InterviewNotesBody";
import { InvestorPitchBody } from "../components/analysis/InvestorPitchBody";
import { MomTestQuestionsBody } from "../components/analysis/MomTestQuestionsBody";
import { MoscowScopeBody } from "../components/analysis/MoscowScopeBody";
import { RiskyAssumptionsBody } from "../components/analysis/RiskyAssumptionsBody";
import { ValidationRoadmapBody } from "../components/analysis/ValidationRoadmapBody";
import { ActiveIdeaPageState } from "../components/ideas/ActiveIdeaPageState";
import { useActiveIdeaId } from "../hooks/useActiveIdeaId";
import { useIdea } from "../hooks/useIdea";
import { ApiError, sendMentorMessage, updateIdea } from "../lib/api";
import type { ChatMessage } from "../types";

const ACTION_LABELS: Record<string, string> = {
  update_target_audience: "Hedef kitle güncellendi",
  regenerate_validation_roadmap: "Yol haritası yenilendi",
  regenerate_moscow_scope: "MVP kapsamı güncellendi",
  generate_mom_test_questions: "Görüşme soruları üretildi",
  regenerate_risky_assumptions: "Riskli varsayımlar güncellendi",
  regenerate_general_evaluation: "Genel değerlendirme güncellendi",
  regenerate_competitor_analysis: "Rakip analizi güncellendi",
  generate_investor_pitch: "Yatırımcı sunumu hazırlandı",
  save_interview_note: "Görüşme notu kaydedildi",
  analyze_interview_evidence: "Görüşme kanıtları analiz edildi",
};

function nowLabel() {
  return new Date().toLocaleTimeString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface AnalysisPageProps {
  onReport: () => void;
}

interface CardHeaderProps {
  bg: string;
  Icon: React.ComponentType<{
    size?: number;
    className?: string;
  }>;
  iconColor: string;
  title: string;
}

export function AnalysisPage({ onReport }: AnalysisPageProps) {
  const [msgs, setMsgs] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Merhaba! Bu fikir üzerinde birlikte çalışalım. Hedef kitleyi, MVP kapsamını, yol haritasını veya müşteri sorularını güncellememi isteyebilirsin.",
      timestamp: nowLabel(),
    },
  ]);

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [roadmapRefreshKey, setRoadmapRefreshKey] = useState(0);
  const [risksRefreshKey, setRisksRefreshKey] = useState(0);
  const [moscowRefreshKey, setMoscowRefreshKey] = useState(0);
  const [questionsRefreshKey, setQuestionsRefreshKey] = useState(0);
  const [evaluationRefreshKey, setEvaluationRefreshKey] = useState(0);
  const [competitorRefreshKey, setCompetitorRefreshKey] = useState(0);
  const [pitchRefreshKey, setPitchRefreshKey] = useState(0);
  const [notesRefreshKey, setNotesRefreshKey] = useState(0);

  const { ideaId, setActiveIdeaId } = useActiveIdeaId();
  const {
    status: ideaStatus,
    data: idea,
    reload: reloadIdea,
  } = useIdea(ideaId);

  const [isEditingIdea, setIsEditingIdea] = useState(false);
  const [isSavingIdea, setIsSavingIdea] = useState(false);
  const [editIdeaError, setEditIdeaError] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
    target_audience: "",
    problem: "",
    solution: "",
    sector: "",
  });

  const startEditingIdea = () => {
    if (!idea) return;
    setEditForm({
      title: idea.title,
      description: idea.description,
      target_audience: idea.target_audience,
      problem: idea.problem,
      solution: idea.solution,
      sector: idea.sector,
    });
    setEditIdeaError(null);
    setIsEditingIdea(true);
  };

  const cancelEditingIdea = () => {
    setIsEditingIdea(false);
    setEditIdeaError(null);
  };

  const handleSaveIdea = async (event: FormEvent) => {
    event.preventDefault();
    if (!idea || isSavingIdea) return;

    setIsSavingIdea(true);
    setEditIdeaError(null);

    try {
      await updateIdea(idea.id, editForm);
      await reloadIdea();
      setIsEditingIdea(false);
    } catch (err) {
      setEditIdeaError(err instanceof ApiError ? err.message : "Fikir güncellenemedi.");
    } finally {
      setIsSavingIdea(false);
    }
  };

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScrollRef = useRef(true);
  const currentIdeaIdRef = useRef(ideaId);
  currentIdeaIdRef.current = ideaId;

  const quickActions = [
    "Riskleri güncelle",
    "MVP'yi sadeleştir",
    "Müşteri soruları üret",
    "Hedef kitleyi değiştir",
    "Yol haritasını yenile",
    "Görüşme notlarını analiz et",
    "Rakip analizini oluştur",
    "Sunumumu hazırla",
  ];

  const sendMsg = async () => {
    const text = input.trim();

    if (
      !text ||
      isSending ||
      ideaId === null ||
      ideaStatus !== "ready" ||
      idea?.id !== ideaId
    ) {
      return;
    }

    const history = msgs.slice(-6).map((message) => ({
      role: message.role,
      content: message.content,
    }));

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: nowLabel(),
    };

    setMsgs((previous) => [...previous, userMsg]);
    setInput("");
    setIsSending(true);

    try {
      const response = await sendMentorMessage(ideaId, text, history);

      if (currentIdeaIdRef.current !== ideaId) {
        return;
      }

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.reply,
        timestamp: nowLabel(),
        actions: response.actions.map((action) => ({
          tool: action.tool,
          status: action.status,
          result: action.result,
        })),
      };

      setMsgs((previous) => [...previous, assistantMsg]);

      if (
        response.actions.some(
          (action) =>
            action.tool === "regenerate_validation_roadmap" &&
            action.status === "success",
        )
      ) {
        setRoadmapRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "regenerate_risky_assumptions" &&
            action.status === "success",
        )
      ) {
        setRisksRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "regenerate_moscow_scope" &&
            action.status === "success",
        )
      ) {
        setMoscowRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "generate_mom_test_questions" &&
            action.status === "success",
        )
      ) {
        setQuestionsRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "regenerate_general_evaluation" &&
            action.status === "success",
        )
      ) {
        setEvaluationRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "update_target_audience" &&
            action.status === "success",
        )
      ) {
        reloadIdea();
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "analyze_interview_evidence" &&
            action.status === "success",
        )
      ) {
        setRisksRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "save_interview_note" && action.status === "success",
        )
      ) {
        setNotesRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "regenerate_competitor_analysis" &&
            action.status === "success",
        )
      ) {
        setCompetitorRefreshKey((key) => key + 1);
      }

      if (
        response.actions.some(
          (action) =>
            action.tool === "generate_investor_pitch" &&
            action.status === "success",
        )
      ) {
        setPitchRefreshKey((key) => key + 1);
      }
    } catch (error) {
      if (currentIdeaIdRef.current !== ideaId) {
        return;
      }

      if (error instanceof ApiError && error.status === 404) {
        void reloadIdea();
      }

      setMsgs((previous) => [
        ...previous,
        {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content:
            error instanceof ApiError && error.status !== 404
              ? error.message
              : "Bir şeyler ters gitti, tekrar dener misin?",
          timestamp: nowLabel(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container || !shouldAutoScrollRef.current) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "auto",
    });
  }, [msgs, isSending]);

  const CardHeader = ({
    bg,
    Icon,
    iconColor,
    title,
  }: CardHeaderProps) => (
    <div className="mb-4 flex items-center gap-2.5">
      <div
        className={`flex h-7 w-7 items-center justify-center rounded-lg border border-border ${bg}`}
      >
        <Icon size={14} className={iconColor} />
      </div>

      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
    </div>
  );

  if (ideaStatus === "loading") {
    return <ActiveIdeaPageState mode="loading" />;
  }

  if (
    ideaId === null ||
    ideaStatus === "idle" ||
    ideaStatus === "not_found"
  ) {
    return <ActiveIdeaPageState mode="empty" />;
  }

  if (ideaStatus === "error") {
    return (
      <ActiveIdeaPageState
        mode="error"
        onRetry={() => void reloadIdea()}
      />
    );
  }

  if (!idea || idea.id !== ideaId) {
    return <ActiveIdeaPageState mode="loading" />;
  }

  return (
    <div
      className="flex min-h-0 flex-1 flex-col overflow-x-hidden overflow-y-auto lg:flex-row lg:overflow-hidden"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      {/* Sol taraf: Analiz */}
      <div className="hide-scroll flex-1 lg:min-h-0 lg:overflow-y-auto">
        <div className="mx-auto max-w-2xl px-6 py-8">
          <div className="mb-7 flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="mb-2.5 flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full border border-border bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground">
                  <Tag size={10} />
                  {idea?.sector || "Sektör belirtilmedi"}
                </span>

                <span className="inline-flex items-center gap-1 rounded-full border border-border bg-secondary px-2.5 py-1 text-xs font-medium text-secondary-foreground">
                  <Users size={10} />
                  {idea?.target_audience || "Hedef kitle belirtilmedi"}
                </span>
              </div>

              <h1 className="text-xl font-bold text-foreground">
                {idea?.title ?? "Yükleniyor..."}
              </h1>

              <p className="mt-1 text-xs text-muted-foreground">
                {idea
                  ? `Oluşturulma: ${new Date(
                      idea.created_at,
                    ).toLocaleDateString("tr-TR")}`
                  : ""}
              </p>
            </div>

            <div className="flex flex-shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={onReport}
                className="inline-flex items-center gap-1.5 rounded-xl border border-border px-3.5 py-2 text-xs font-semibold text-muted-foreground transition-all hover:bg-secondary hover:text-foreground"
              >
                <FileText size={12} />
                Doğrulama Raporu
              </button>

              <button
                type="button"
                disabled
                title="Backend entegrasyonu sonrasında kullanılabilir"
                className="inline-flex cursor-not-allowed items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground opacity-45"
              >
                <RefreshCw size={12} />
                Raporu Yenile
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {/* Fikir özeti */}
            <div className="relative rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-accent"
                Icon={Sparkles}
                iconColor="text-accent-foreground"
                title="Fikir Özeti"
              />

              {!isEditingIdea && (
                <button
                  type="button"
                  onClick={startEditingIdea}
                  className="absolute right-5 top-5 inline-flex items-center gap-1 text-[11px] font-semibold text-muted-foreground transition-colors hover:text-foreground"
                >
                  <Pencil size={11} />
                  Düzenle
                </button>
              )}

              {isEditingIdea ? (
                <form onSubmit={handleSaveIdea} className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-muted-foreground">Başlık</label>
                    <input
                      type="text"
                      required
                      value={editForm.title}
                      onChange={(e) => setEditForm((f) => ({ ...f, title: e.target.value }))}
                      className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                    />
                  </div>

                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-muted-foreground">Sektör</label>
                      <input
                        type="text"
                        value={editForm.sector}
                        onChange={(e) => setEditForm((f) => ({ ...f, sector: e.target.value }))}
                        className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-muted-foreground">Hedef Kitle</label>
                      <input
                        type="text"
                        value={editForm.target_audience}
                        onChange={(e) => setEditForm((f) => ({ ...f, target_audience: e.target.value }))}
                        className="w-full rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-muted-foreground">Açıklama</label>
                    <textarea
                      required
                      rows={3}
                      value={editForm.description}
                      onChange={(e) => setEditForm((f) => ({ ...f, description: e.target.value }))}
                      className="w-full resize-none rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-muted-foreground">Problem</label>
                    <textarea
                      rows={2}
                      value={editForm.problem}
                      onChange={(e) => setEditForm((f) => ({ ...f, problem: e.target.value }))}
                      className="w-full resize-none rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-muted-foreground">Çözüm Önerisi</label>
                    <textarea
                      rows={2}
                      value={editForm.solution}
                      onChange={(e) => setEditForm((f) => ({ ...f, solution: e.target.value }))}
                      className="w-full resize-none rounded-xl border border-border bg-muted px-3.5 py-2.5 text-sm text-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20"
                    />
                  </div>

                  {editIdeaError && (
                    <p className="text-xs text-destructive">{editIdeaError}</p>
                  )}

                  <div className="flex items-center gap-3">
                    <button
                      type="submit"
                      disabled={isSavingIdea}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground transition-all hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {isSavingIdea ? "Kaydediliyor..." : "Kaydet"}
                    </button>
                    <button
                      type="button"
                      onClick={cancelEditingIdea}
                      className="text-xs font-semibold text-muted-foreground transition-colors hover:text-foreground"
                    >
                      Vazgeç
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {idea?.description}
                  </p>

                  {idea?.problem && (
                    <div className="mt-3 border-t border-border pt-3">
                      <span className="text-xs font-bold text-foreground">
                        Problem:{" "}
                      </span>

                      <span className="text-sm text-muted-foreground">
                        {idea.problem}
                      </span>
                    </div>
                  )}

                  {idea?.solution && (
                    <div className="mt-2">
                      <span className="text-xs font-bold text-foreground">
                        Çözüm Önerisi:{" "}
                      </span>

                      <span className="text-sm text-muted-foreground">
                        {idea.solution}
                      </span>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Riskli varsayımlar */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={AlertTriangle}
                iconColor="text-destructive"
                title="Riskli Varsayımlar"
              />

              <RiskyAssumptionsBody
                key={risksRefreshKey}
                ideaId={ideaId}
              />
            </div>

            {/* Görüşme notları */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={ClipboardList}
                iconColor="text-foreground"
                title="Görüşme Notları"
              />

              <InterviewNotesBody
                ideaId={ideaId}
                refreshToken={notesRefreshKey}
              />
            </div>

            {/* Mom Test soruları */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={MessageSquare}
                iconColor="text-foreground"
                title="Mom Test / Müşteri Görüşme Soruları"
              />

              <MomTestQuestionsBody
                key={questionsRefreshKey}
                ideaId={ideaId}
              />
            </div>

            {/* MVP kapsamı */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={Target}
                iconColor="text-foreground"
                title="MVP Kapsamı"
              />

              <MoscowScopeBody
                key={moscowRefreshKey}
                ideaId={ideaId}
              />
            </div>

            {/* Doğrulama yol haritası */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={Map}
                iconColor="text-foreground"
                title="Doğrulama Yol Haritası"
              />

              <ValidationRoadmapBody
                key={roadmapRefreshKey}
                ideaId={ideaId}
                onIdeaIdChange={setActiveIdeaId}
              />
            </div>

            {/* Genel değerlendirme */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={Star}
                iconColor="text-foreground"
                title="Genel Değerlendirme"
              />

              <GeneralEvaluationBody
                key={evaluationRefreshKey}
                ideaId={ideaId}
              />
            </div>

            {/* Rakip / Pazar Analizi */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={TrendingUp}
                iconColor="text-foreground"
                title="Rakip / Pazar Analizi"
              />

              <CompetitorAnalysisBody
                key={competitorRefreshKey}
                ideaId={ideaId}
              />
            </div>

            {/* Yatırımcı Sunumu */}
            <div className="rounded-xl border border-border bg-card p-5">
              <CardHeader
                bg="bg-muted"
                Icon={Megaphone}
                iconColor="text-foreground"
                title="Yatırımcı Sunumu"
              />

              <InvestorPitchBody
                key={pitchRefreshKey}
                ideaId={ideaId}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Sağ taraf: AI sohbet */}
      <div className="flex min-h-[480px] w-full flex-shrink-0 flex-col border-t border-border bg-card lg:h-full lg:min-h-0 lg:w-[320px] lg:border-l lg:border-t-0">
        <div className="shrink-0 border-b border-border px-4 py-4">
          <div className="mb-2 flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary">
              <Bot size={13} className="text-primary-foreground" />
            </div>

            <span className="text-sm font-bold text-foreground">
              AI Fikir Asistanı
            </span>
          </div>

          <p className="text-xs leading-relaxed text-muted-foreground">
            Bu fikir üzerinde birlikte çalışalım. Hedef kitleyi, MVP&apos;yi,
            riskleri veya müşteri sorularını güncelleyebilirim.
          </p>
        </div>

        {/* Hızlı aksiyonlar */}
        <div className="flex shrink-0 flex-wrap gap-1.5 border-b border-border px-3 py-3">
          {quickActions.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => setInput(action)}
              disabled={isSending}
              className="rounded-full border border-border px-2.5 py-1 text-[11px] text-muted-foreground transition-all hover:border-foreground/20 hover:bg-accent hover:text-foreground disabled:pointer-events-none disabled:opacity-40"
            >
              {action}
            </button>
          ))}
        </div>

        {/* Mesajlar */}
        <div
          ref={messagesContainerRef}
          onScroll={(event) => {
            const container = event.currentTarget;
            const distanceFromBottom =
              container.scrollHeight -
              container.scrollTop -
              container.clientHeight;
            shouldAutoScrollRef.current = distanceFromBottom < 80;
          }}
          className="hide-scroll min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-4"
        >
          {msgs.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}
            >
              {message.role === "assistant" && (
                <div className="mr-2 mt-1 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary">
                  <Bot size={11} className="text-primary-foreground" />
                </div>
              )}

              <div className="max-w-[220px]">
                <div
                  className={`whitespace-pre-line px-3.5 py-2.5 text-sm leading-relaxed ${
                    message.role === "user"
                      ? "rounded-2xl rounded-tr-sm bg-primary text-primary-foreground"
                      : "rounded-2xl rounded-tl-sm border border-border bg-secondary text-secondary-foreground"
                  }`}
                >
                  {message.content}
                </div>

                {message.actions && message.actions.length > 0 && (
                  <div className="mt-1.5 flex flex-col gap-1.5">
                    {message.actions.map((action, index) => {
                      const questions =
                        action.status === "success"
                          ? (action.result?.questions as
                              | string[]
                              | undefined)
                          : undefined;

                      const newAudience =
                        action.status === "success"
                          ? (action.result?.target_audience as
                              | string
                              | undefined)
                          : undefined;

                      const evidenceSummary =
                        action.status === "success" &&
                        action.tool === "analyze_interview_evidence"
                          ? (action.result as {
                              validated_count?: number;
                              refuted_count?: number;
                              untested_count?: number;
                              new_assumptions_count?: number;
                            } | undefined)
                          : undefined;

                      return (
                        <div
                          key={`${action.tool}-${index}`}
                          className="flex flex-col items-start gap-1"
                        >
                          <span
                            className={`inline-flex w-fit items-center gap-1.5 rounded-lg border px-2 py-1 text-[11px] font-semibold ${
                              action.status === "success"
                                ? "border-success/40 bg-success/10 text-success"
                                : "border-destructive/40 bg-destructive/10 text-destructive"
                            }`}
                          >
                            {action.status === "success" ? (
                              <CheckCircle2 size={11} />
                            ) : (
                              <XCircle size={11} />
                            )}

                            {ACTION_LABELS[action.tool] ?? action.tool}
                          </span>

                          {newAudience && (
                            <span className="rounded-lg border border-border bg-secondary px-2.5 py-1.5 text-xs text-secondary-foreground">
                              &quot;{newAudience}&quot;
                            </span>
                          )}

                          {evidenceSummary && (
                            <span className="rounded-lg border border-border bg-secondary px-2.5 py-1.5 text-xs text-secondary-foreground">
                              ✅ {evidenceSummary.validated_count ?? 0} doğrulandı · ❌{" "}
                              {evidenceSummary.refuted_count ?? 0} çürütüldü · ⏳{" "}
                              {evidenceSummary.untested_count ?? 0} test edilmedi
                              {evidenceSummary.new_assumptions_count
                                ? ` · +${evidenceSummary.new_assumptions_count} yeni`
                                : ""}
                            </span>
                          )}

                          {questions && questions.length > 0 && (
                            <ul className="w-full space-y-1 rounded-lg border border-border bg-secondary px-2.5 py-2">
                              {questions.map((question, questionIndex) => (
                                <li
                                  key={`${question}-${questionIndex}`}
                                  className="flex gap-1.5 text-xs leading-relaxed text-secondary-foreground"
                                >
                                  <span className="font-bold text-foreground">
                                    {questionIndex + 1}.
                                  </span>

                                  {question}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                <div className="mt-1 px-1 text-[10px] text-muted-foreground">
                  {message.timestamp}
                </div>
              </div>
            </div>
          ))}

          {isSending && (
            <div className="flex justify-start">
              <div className="mr-2 mt-1 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary">
                <Bot size={11} className="text-primary-foreground" />
              </div>

              <div className="rounded-2xl rounded-tl-sm border border-border bg-secondary px-3.5 py-2.5 text-sm text-muted-foreground">
                <RefreshCw size={13} className="animate-spin" />
              </div>
            </div>
          )}

        </div>

        {/* Mesaj giriş alanı */}
        <div className="shrink-0 border-t border-border px-4 py-3">
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey &&
                  !event.nativeEvent.isComposing &&
                  event.keyCode !== 229
                ) {
                  event.preventDefault();
                  void sendMsg();
                }
              }}
              placeholder="Bu fikirle ilgili neyi geliştirmek istiyorsun?"
              rows={2}
              disabled={isSending}
              className="flex-1 resize-none rounded-xl border border-border bg-muted px-3 py-2.5 text-xs text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20 disabled:opacity-60"
            />

            <button
              type="button"
              onClick={() => void sendMsg()}
              disabled={!input.trim() || isSending}
              aria-label="Mesaj gönder"
              className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground transition-all hover:bg-primary-hover disabled:opacity-40"
            >
              <Send size={13} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
