import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, HelpCircle, Zap, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { analysisData, initialMessages, sampleIdeas } from "../data/mockData";
import type { ChatMessage } from "../types";
import { RiskBadge, StatusBadge } from "../components/common/Badges";
import { MentorCharacter } from "../components/mentor/MentorCharacter";

export function MentorPage({ onAnalyze }: { onAnalyze: () => void }) {
  type MsgRole = "user" | "ai";
  const [msgs, setMsgs] = useState<{ role: MsgRole; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [showAnalyze, setShowAnalyze] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScrollRef = useRef(true);

  const suggestions = [
    "Restoranlar için AI destekli stok yönetimi uygulaması",
    "Freelancer'lar için proje ve fatura takip platformu",
    "Girişimciler için interaktif iş planı oluşturma aracı",
    "E-ticaret satıcıları için fiyat optimizasyon motoru",
  ];

  const send = (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || isSending) return;
    setInput("");
    setIsSending(true);
    setMsgs((p) => [...p, { role: "user" as const, text: msg }]);
    setTimeout(() => {
      setMsgs((p) => [
        ...p,
        {
          role: "ai" as const,
          text: "Bu fikir ilginç! Hedef kitlenizi, yaşanan problemi ve önerdiğiniz çözümü daha iyi anlarsam çok daha kapsamlı bir analiz hazırlayabilirim. Fikrinizle ilgili birkaç ek bilgi verebilir misiniz?",
        },
      ]);
      setShowAnalyze(true);
      setIsSending(false);
    }, 900);
  };

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container || !shouldAutoScrollRef.current) return;

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "auto",
    });
  }, [msgs, isSending]);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-x-hidden md:flex-row md:overflow-hidden" style={{ animation: "page-in 0.3s ease-out" }}>

      {/* Left: Character */}
      <div className="flex-shrink-0 md:w-[44%] flex flex-col items-center justify-center py-5 md:py-8 px-4 md:px-6 relative border-b md:border-b-0 md:border-r border-border">
        {/* Glow rings */}
        <div className="relative" style={{ width: 260, height: 300 }}>
          <div
            className="absolute rounded-full border border-dashed"
            style={{
              width: 220, height: 220,
              borderColor: "var(--border)",
              top: "50%", left: "50%",
              animation: "ring-cw 16s linear infinite, ring-pulse 4s ease-in-out infinite",
              transform: "translate(-50%,-50%) translateY(-18px)",
            }}
          />
          <div
            className="absolute rounded-full border"
            style={{
              width: 250, height: 250,
              borderColor: "var(--surface-elevated)",
              top: "50%", left: "50%",
              animation: "ring-ccw 24s linear infinite",
              transform: "translate(-50%,-50%) translateY(-18px)",
            }}
          />
          {/* Glow halo */}
          <div
            className="absolute rounded-full pointer-events-none"
            style={{
              width: 180, height: 180,
              background: "radial-gradient(circle, var(--accent) 0%, transparent 70%)",
              top: "50%", left: "50%",
              transform: "translate(-50%, -65%)",
            }}
          />
          {/* Character */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 mentor-enter">\n            <div className="mentor-float"><MentorCharacter /></div>
          </div>
        </div>

        {/* Label */}
        <div className="text-center mt-1">
          <p className="text-sm font-semibold text-primary">FikirLab Asistanı</p>
          <p className="text-xs text-muted-foreground mt-0.5">Girişim Mentörünüz</p>
        </div>
      </div>

      {/* Right: Chat area */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Greeting / chat messages */}
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
          className="hide-scroll min-h-0 flex-1 overflow-y-auto px-5 pt-6 pb-2"
        >
          {/* Always-visible greeting bubble */}
          <div className="bg-secondary border border-border rounded-2xl rounded-tl-sm p-4 mb-5" style={{ animation: "mentor-enter 0.6s ease-out" }}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                <Bot size={11} className="text-primary-foreground" />
              </div>
              <span className="text-xs font-semibold text-primary">FikirLab Asistanı</span>
            </div>
            <p className="text-sm text-foreground leading-relaxed">
              Merhaba! Ben FikirLab Asistanı. İş fikrinizi analiz etmek, riskli varsayımları belirlemek ve doğrulama yol haritanızı oluşturmak için buradayım.
            </p>
            <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
              Fikrinizi birkaç cümleyle anlatın; sizi analiz aşamasına yönlendireyim. 👇
            </p>
          </div>

          {/* Conversation messages */}
          <div className="space-y-3">
            {msgs.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                {m.role === "ai" && (
                  <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                    <Bot size={11} className="text-primary-foreground" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-sm"
                      : "bg-secondary border border-border text-foreground rounded-tl-sm"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}

            {showAnalyze && (
              <div className="flex justify-start pt-1">
                <button
                  type="button"
                  onClick={onAnalyze}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-hover text-primary-foreground text-sm font-semibold rounded-xl transition-all"
                  style={{ animation: "step-appear 0.4s ease-out" }}
                >
                  <Sparkles size={14} />Fikri Analiz Et<ArrowRight size={13} />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Suggestion chips */}
        {msgs.length === 0 && (
          <div className="px-5 pb-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setInput(s)}
                disabled={isSending}
                className="text-left text-xs px-3.5 py-2.5 rounded-xl border border-border bg-muted text-muted-foreground hover:text-accent-foreground hover:border-accent-foreground/40 hover:bg-accent transition-all leading-relaxed"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="px-5 py-4 border-t border-border">
          <div className="flex items-end gap-2.5">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey &&
                  !event.nativeEvent.isComposing &&
                  event.keyCode !== 229
                ) {
                  event.preventDefault();
                  send();
                }
              }}
              placeholder="İş fikrinizi birkaç cümleyle anlatın..."
              rows={2}
              className="flex-1 bg-muted border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 resize-none transition-all"
            />
            <button
              type="button"
              onClick={() => send()}
              disabled={!input.trim() || isSending}
              aria-label="Mesaj gönder"
              className="w-11 h-11 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl flex items-center justify-center transition-all disabled:opacity-40 flex-shrink-0"
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
