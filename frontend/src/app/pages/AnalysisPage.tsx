import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle2, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, XCircle, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { sampleIdeas } from "../data/mockData";
import type { ChatMessage } from "../types";
import { StatusBadge } from "../components/common/Badges";
import { MentorCharacter } from "../components/mentor/MentorCharacter";
import { ValidationRoadmapBody } from "../components/analysis/ValidationRoadmapBody";
import { RiskyAssumptionsBody } from "../components/analysis/RiskyAssumptionsBody";
import { MoscowScopeBody } from "../components/analysis/MoscowScopeBody";
import { MomTestQuestionsBody } from "../components/analysis/MomTestQuestionsBody";
import { GeneralEvaluationBody } from "../components/analysis/GeneralEvaluationBody";
import { useActiveIdeaId } from "../hooks/useActiveIdeaId";
import { useIdea } from "../hooks/useIdea";
import { ApiError, sendMentorMessage } from "../lib/api";

const ACTION_LABELS: Record<string, string> = {
  update_target_audience: "Hedef kitle güncellendi",
  regenerate_validation_roadmap: "Yol haritası yenilendi",
  regenerate_moscow_scope: "MVP kapsamı güncellendi",
  generate_mom_test_questions: "Görüşme soruları üretildi",
  regenerate_risky_assumptions: "Riskli varsayımlar güncellendi",
  regenerate_general_evaluation: "Genel değerlendirme güncellendi",
};

function nowLabel() {
  return new Date().toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
}

export function AnalysisPage({ onReport }: { onReport: () => void }) {
  const [msgs, setMsgs] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Merhaba! Bu fikir üzerinde birlikte çalışalım. Hedef kitleyi, MVP kapsamını, yol haritasını veya müşteri sorularını güncellememi isteyebilirsin.",
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
  const [ideaId, setIdeaId] = useActiveIdeaId();
  const { data: idea, reload: reloadIdea } = useIdea(ideaId);
  const endRef = useRef<HTMLDivElement>(null);

  const sendMsg = async () => {
    const text = input.trim();
    if (!text || isSending) return;

    const history = msgs.slice(-6).map((m) => ({ role: m.role, content: m.content }));
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", content: text, timestamp: nowLabel() };
    setMsgs((p) => [...p, userMsg]);
    setInput("");
    setIsSending(true);

    try {
      const res = await sendMentorMessage(ideaId, text, history);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.reply,
        timestamp: nowLabel(),
        actions: res.actions.map((a) => ({ tool: a.tool, status: a.status, result: a.result })),
      };
      setMsgs((p) => [...p, assistantMsg]);

      if (res.actions.some((a) => a.tool === "regenerate_validation_roadmap" && a.status === "success")) {
        setRoadmapRefreshKey((k) => k + 1);
      }
      if (res.actions.some((a) => a.tool === "regenerate_risky_assumptions" && a.status === "success")) {
        setRisksRefreshKey((k) => k + 1);
      }
      if (res.actions.some((a) => a.tool === "regenerate_moscow_scope" && a.status === "success")) {
        setMoscowRefreshKey((k) => k + 1);
      }
      if (res.actions.some((a) => a.tool === "generate_mom_test_questions" && a.status === "success")) {
        setQuestionsRefreshKey((k) => k + 1);
      }
      if (res.actions.some((a) => a.tool === "regenerate_general_evaluation" && a.status === "success")) {
        setEvaluationRefreshKey((k) => k + 1);
      }
      if (res.actions.some((a) => a.tool === "update_target_audience" && a.status === "success")) {
        reloadIdea();
      }
    } catch (err) {
      setMsgs((p) => [
        ...p,
        {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content: err instanceof ApiError ? err.message : "Bir şeyler ters gitti, tekrar dener misin?",
          timestamp: nowLabel(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, isSending]);

  const quickActions = ["Riskleri güncelle", "MVP'yi sadeleştir", "Müşteri soruları üret", "Hedef kitleyi değiştir", "Yol haritasını yenile"];

  const CardHeader = ({ bg, Icon, iconColor, title }: { bg: string; Icon: any; iconColor: string; title: string }) => (
    <div className="flex items-center gap-2.5 mb-4">
      <div className={`w-7 h-7 rounded-lg ${bg} flex items-center justify-center border border-white/5`}>
        <Icon size={14} className={iconColor} />
      </div>
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col lg:flex-row min-h-0 overflow-x-hidden lg:overflow-hidden" style={{ animation: "page-in 0.3s ease-out" }}>
      {/* Left: Analysis */}
      <div className="flex-1 overflow-y-auto hide-scroll">
        <div className="max-w-2xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-7">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2.5">
                <span className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 bg-violet-500/10 text-violet-400 rounded-full border border-violet-500/20">
                  <Tag size={10} />{idea?.sector || "Sektör belirtilmedi"}
                </span>
                <span className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 bg-secondary text-muted-foreground rounded-full border border-border">
                  <Users size={10} />{idea?.target_audience || "Hedef kitle belirtilmedi"}
                </span>
              </div>
              <h1 className="text-xl font-bold text-foreground">{idea?.title ?? "Yükleniyor..."}</h1>
              <p className="text-xs text-muted-foreground mt-1">
                {idea ? `Oluşturulma: ${new Date(idea.created_at).toLocaleDateString("tr-TR")}` : ""}
              </p>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <button onClick={onReport} className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-border text-muted-foreground hover:text-foreground hover:bg-secondary transition-all">
                <FileText size={12} />Doğrulama Raporu
              </button>
              <button disabled title="Backend entegrasyonu sonrasında kullanılabilir" className="inline-flex cursor-not-allowed items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-primary text-white opacity-45">
                <RefreshCw size={12} />Raporu Yenile
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {/* A: Summary */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-blue-500/10" Icon={Sparkles} iconColor="text-blue-400" title="Fikir Özeti" />
              <p className="text-sm text-muted-foreground leading-relaxed">{idea?.description}</p>
              {idea?.problem && (
                <div className="mt-3 pt-3 border-t border-border">
                  <span className="text-xs font-bold text-foreground">Problem: </span>
                  <span className="text-sm text-muted-foreground">{idea.problem}</span>
                </div>
              )}
              {idea?.solution && (
                <div className="mt-2">
                  <span className="text-xs font-bold text-foreground">Çözüm Önerisi: </span>
                  <span className="text-sm text-muted-foreground">{idea.solution}</span>
                </div>
              )}
            </div>

            {/* B: Risks */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-red-500/10" Icon={AlertTriangle} iconColor="text-red-400" title="Riskli Varsayımlar" />
              <RiskyAssumptionsBody key={risksRefreshKey} ideaId={ideaId} />
            </div>

            {/* C: Questions */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-cyan-500/10" Icon={MessageSquare} iconColor="text-cyan-400" title="Mom Test / Müşteri Görüşme Soruları" />
              <MomTestQuestionsBody key={questionsRefreshKey} ideaId={ideaId} />
            </div>

            {/* D: MVP MoSCoW */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-emerald-500/10" Icon={Target} iconColor="text-emerald-400" title="MVP Kapsamı" />
              <MoscowScopeBody key={moscowRefreshKey} ideaId={ideaId} />
            </div>

            {/* E: Roadmap */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-violet-500/10" Icon={Map} iconColor="text-violet-400" title="Doğrulama Yol Haritası" />
              <ValidationRoadmapBody key={roadmapRefreshKey} ideaId={ideaId} onIdeaIdChange={setIdeaId} />
            </div>

            {/* F: Evaluation */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-amber-500/10" Icon={Star} iconColor="text-amber-400" title="Genel Değerlendirme" />
              <GeneralEvaluationBody key={evaluationRefreshKey} ideaId={ideaId} />
            </div>
          </div>
        </div>
      </div>

      {/* Right: AI Chat */}
      <div className="w-full lg:w-[320px] min-h-[480px] lg:min-h-0 flex-shrink-0 border-t lg:border-t-0 lg:border-l border-border flex flex-col bg-card">
        <div className="px-4 py-4 border-b border-border">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
              <Bot size={13} className="text-white" />
            </div>
            <span className="text-sm font-bold text-foreground">AI Fikir Asistanı</span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Bu fikir üzerinde birlikte çalışalım. Hedef kitleyi, MVP'yi, riskleri veya müşteri sorularını güncelleyebilirim.
          </p>
        </div>

        {/* Quick actions */}
        <div className="px-3 py-3 border-b border-border flex flex-wrap gap-1.5">
          {quickActions.map((a) => (
            <button
              key={a}
              onClick={() => setInput(a)}
              disabled={isSending}
              className="text-[11px] px-2.5 py-1 rounded-full border border-border text-muted-foreground hover:text-foreground hover:border-blue-500/40 hover:bg-secondary transition-all disabled:opacity-40 disabled:pointer-events-none"
            >
              {a}
            </button>
          ))}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto hide-scroll px-4 py-4 space-y-4">
          {msgs.map((m) => (
            <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              {m.role === "assistant" && (
                <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mr-2 mt-1">
                  <Bot size={11} className="text-white" />
                </div>
              )}
              <div className="max-w-[220px]">
                <div className={`px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-line ${
                  m.role === "user"
                    ? "bg-primary text-white rounded-2xl rounded-tr-sm"
                    : "bg-secondary border border-border text-foreground rounded-2xl rounded-tl-sm"
                }`}>
                  {m.content}
                </div>
                {m.actions && m.actions.length > 0 && (
                  <div className="mt-1.5 flex flex-col gap-1.5">
                    {m.actions.map((a, i) => {
                      const questions = a.status === "success" ? (a.result?.questions as string[] | undefined) : undefined;
                      const newAudience = a.status === "success" ? (a.result?.target_audience as string | undefined) : undefined;

                      return (
                        <div key={i} className="flex flex-col gap-1 items-start">
                          <span
                            className={`inline-flex items-center gap-1.5 text-[11px] font-semibold px-2 py-1 rounded-lg border w-fit ${
                              a.status === "success"
                                ? "text-emerald-400 border-emerald-800/40 bg-emerald-900/10"
                                : "text-red-400 border-red-800/40 bg-red-900/10"
                            }`}
                          >
                            {a.status === "success" ? <CheckCircle2 size={11} /> : <XCircle size={11} />}
                            {ACTION_LABELS[a.tool] ?? a.tool}
                          </span>

                          {newAudience && (
                            <span className="text-xs text-foreground bg-secondary border border-border rounded-lg px-2.5 py-1.5">
                              "{newAudience}"
                            </span>
                          )}

                          {questions && questions.length > 0 && (
                            <ul className="w-full space-y-1 bg-secondary border border-border rounded-lg px-2.5 py-2">
                              {questions.map((q, qi) => (
                                <li key={qi} className="text-xs text-foreground leading-relaxed flex gap-1.5">
                                  <span className="text-blue-400 font-bold">{qi + 1}.</span>{q}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
                <div className="text-[10px] text-muted-foreground mt-1 px-1">{m.timestamp}</div>
              </div>
            </div>
          ))}
          {isSending && (
            <div className="flex justify-start">
              <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mr-2 mt-1">
                <Bot size={11} className="text-white" />
              </div>
              <div className="px-3.5 py-2.5 text-sm bg-secondary border border-border text-muted-foreground rounded-2xl rounded-tl-sm">
                <RefreshCw size={13} className="animate-spin" />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input */}
        <div className="px-4 py-3 border-t border-border">
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMsg(); } }}
              placeholder="Bu fikirle ilgili neyi geliştirmek istiyorsun?"
              rows={2}
              disabled={isSending}
              className="flex-1 bg-muted border border-border rounded-xl px-3 py-2.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 resize-none transition-all disabled:opacity-60"
            />
            <button
              onClick={sendMsg}
              disabled={!input.trim() || isSending}
              className="w-9 h-9 bg-primary hover:bg-blue-600 text-white rounded-xl flex items-center justify-center transition-all disabled:opacity-40 flex-shrink-0"
            >
              <Send size={13} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
