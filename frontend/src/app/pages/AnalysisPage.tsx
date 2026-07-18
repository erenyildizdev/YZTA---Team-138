import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, HelpCircle, Zap, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { analysisData, initialMessages, sampleIdeas } from "../data/mockData";
import type { ChatMessage } from "../types";
import { RiskBadge, StatusBadge } from "../components/common/Badges";
import { MentorCharacter } from "../components/mentor/MentorCharacter";

export function AnalysisPage({ onReport }: { onReport: () => void }) {
  const [msgs, setMsgs] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  const sendMsg = () => {
    if (!input.trim()) return;
    const u: ChatMessage = { id: Date.now().toString(), role: "user", content: input, timestamp: new Date().toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }) };
    setMsgs((p) => [...p, u]);
    setInput("");
    setTimeout(() => {
      setMsgs((p) => [
        ...p,
        { id: (Date.now() + 1).toString(), role: "assistant", content: "Bu önerin analizi etkiliyor. Hedef kitleyi ve problem tanımını güncelleyip yeni bir risk değerlendirmesi yapabilirim.", timestamp: new Date().toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }), hasAction: true },
      ]);
    }, 900);
  };

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

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
                  <Tag size={10} />F&B Teknolojisi
                </span>
                <span className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 bg-secondary text-muted-foreground rounded-full border border-border">
                  <Users size={10} />Restoran sahipleri
                </span>
              </div>
              <h1 className="text-xl font-bold text-foreground">Restoran Stok Yönetim Uygulaması</h1>
              <p className="text-xs text-muted-foreground mt-1">Son güncelleme: 28 Haziran 2025</p>
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
              <p className="text-sm text-muted-foreground leading-relaxed">{analysisData.summary}</p>
            </div>

            {/* B: Risks */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-red-500/10" Icon={AlertTriangle} iconColor="text-red-400" title="Riskli Varsayımlar" />
              <div className="space-y-3">
                {analysisData.risks.map((r) => (
                  <div key={r.id} className="flex items-start gap-3">
                    <RiskBadge level={r.level} />
                    <p className="text-sm text-muted-foreground leading-relaxed">{r.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* C: Questions */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-cyan-500/10" Icon={MessageSquare} iconColor="text-cyan-400" title="Mom Test / Müşteri Görüşme Soruları" />
              <div className="space-y-2.5">
                {analysisData.questions.map((q, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5 border border-blue-500/20">{i + 1}</span>
                    <p className="text-sm text-muted-foreground">{q}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* D: MVP MoSCoW */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-emerald-500/10" Icon={Target} iconColor="text-emerald-400" title="MVP Kapsamı" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { key: "mustHave",   label: "Must Have",   bg: "bg-red-900/20 border-red-800/30",     lc: "text-red-400",     dot: "bg-red-500" },
                  { key: "shouldHave", label: "Should Have", bg: "bg-amber-900/20 border-amber-800/30",   lc: "text-amber-400",   dot: "bg-amber-500" },
                  { key: "couldHave",  label: "Could Have",  bg: "bg-blue-900/20 border-blue-800/30",     lc: "text-blue-400",    dot: "bg-blue-500" },
                  { key: "wontHave",   label: "Won't Have",  bg: "bg-slate-800/30 border-slate-700/30",   lc: "text-slate-400",   dot: "bg-slate-500" },
                ].map(({ key, label, bg, lc, dot }) => (
                  <div key={key} className={`rounded-xl border p-3.5 ${bg}`}>
                    <div className="flex items-center gap-1.5 mb-2.5">
                      <div className={`w-1.5 h-1.5 rounded-full ${dot}`} />
                      <span className={`text-xs font-bold ${lc}`}>{label}</span>
                    </div>
                    <ul className="space-y-1.5">
                      {(analysisData.mvp as any)[key].map((item: string, i: number) => (
                        <li key={i} className={`text-xs leading-relaxed ${lc} opacity-75`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* E: Roadmap */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-violet-500/10" Icon={Map} iconColor="text-violet-400" title="Doğrulama Yol Haritası" />
              {analysisData.roadmap.map((item, i) => (
                <div key={item.step} className="flex gap-3.5">
                  <div className="flex flex-col items-center">
                    <div className="w-7 h-7 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center flex-shrink-0">{item.step}</div>
                    {i < analysisData.roadmap.length - 1 && <div className="w-px flex-1 bg-border mt-1 mb-1" style={{ minHeight: 20 }} />}
                  </div>
                  <div className={`flex-1 ${i < analysisData.roadmap.length - 1 ? "pb-4" : ""}`}>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-foreground">{item.title}</span>
                      <span className="text-xs text-muted-foreground px-2 py-0.5 bg-secondary rounded-full border border-border">{item.weeks}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* F: Evaluation */}
            <div className="bg-card rounded-xl border border-border p-5">
              <CardHeader bg="bg-amber-500/10" Icon={Star} iconColor="text-amber-400" title="Genel Değerlendirme" />
              <div className="space-y-4">
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <CheckCircle size={12} className="text-emerald-400" />
                    <span className="text-xs font-bold text-foreground">Güçlü Yönler</span>
                  </div>
                  <ul className="space-y-1.5">
                    {analysisData.evaluation.strengths.map((s, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-emerald-500 mt-0.5">·</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <HelpCircle size={12} className="text-amber-400" />
                    <span className="text-xs font-bold text-foreground">Belirsiz Noktalar</span>
                  </div>
                  <ul className="space-y-1.5">
                    {analysisData.evaluation.uncertainties.map((u, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-amber-500 mt-0.5">·</span>{u}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-blue-900/20 border border-blue-800/30 rounded-xl p-4">
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <Zap size={12} className="text-blue-400" />
                    <span className="text-xs font-bold text-blue-300">İlk Yapılacak Aksiyon</span>
                  </div>
                  <p className="text-sm text-blue-300/80 leading-relaxed">{analysisData.evaluation.nextAction}</p>
                </div>
              </div>
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
              className="text-[11px] px-2.5 py-1 rounded-full border border-border text-muted-foreground hover:text-foreground hover:border-blue-500/40 hover:bg-secondary transition-all"
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
                {m.hasAction && (
                  <button disabled title="Backend entegrasyonu sonrasında kullanılabilir" className="mt-2 w-full cursor-not-allowed text-xs font-semibold text-blue-400/45 border border-blue-500/15 rounded-xl py-1.5">
                    Analizi Güncelle
                  </button>
                )}
                <div className="text-[10px] text-muted-foreground mt-1 px-1">{m.timestamp}</div>
              </div>
            </div>
          ))}
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
              className="flex-1 bg-muted border border-border rounded-xl px-3 py-2.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 resize-none transition-all"
            />
            <button
              onClick={sendMsg}
              disabled={!input.trim()}
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
