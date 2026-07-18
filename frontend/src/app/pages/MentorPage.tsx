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
  const endRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    "Restoranlar için AI destekli stok yönetimi uygulaması",
    "Freelancer'lar için proje ve fatura takip platformu",
    "Girişimciler için interaktif iş planı oluşturma aracı",
    "E-ticaret satıcıları için fiyat optimizasyon motoru",
  ];

  const send = (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg) return;
    setInput("");
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
    }, 900);
  };

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  return (
    <div className="flex-1 flex flex-col md:flex-row overflow-x-hidden md:overflow-hidden" style={{ animation: "page-in 0.3s ease-out" }}>

      {/* Left: Character */}
      <div className="flex-shrink-0 md:w-[44%] flex flex-col items-center justify-center py-5 md:py-8 px-4 md:px-6 relative border-b md:border-b-0 md:border-r border-border">
        {/* Glow rings */}
        <div className="relative" style={{ width: 260, height: 300 }}>
          <div
            className="absolute rounded-full border border-dashed"
            style={{
              width: 220, height: 220,
              borderColor: "rgba(37,99,235,0.28)",
              top: "50%", left: "50%",
              animation: "ring-cw 16s linear infinite, ring-pulse 4s ease-in-out infinite",
              transform: "translate(-50%,-50%) translateY(-18px)",
            }}
          />
          <div
            className="absolute rounded-full border"
            style={{
              width: 250, height: 250,
              borderColor: "rgba(37,99,235,0.13)",
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
              background: "radial-gradient(circle, rgba(37,99,235,0.22) 0%, transparent 70%)",
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
          <p className="text-sm font-semibold text-blue-400">FikirLab Asistanı</p>
          <p className="text-xs text-muted-foreground mt-0.5">Girişim Mentörünüz</p>
        </div>
      </div>

      {/* Right: Chat area */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Greeting / chat messages */}
        <div className="flex-1 overflow-y-auto hide-scroll px-5 pt-6 pb-2">
          {/* Always-visible greeting bubble */}
          <div className="bg-secondary border border-border rounded-2xl rounded-tl-sm p-4 mb-5" style={{ animation: "mentor-enter 0.6s ease-out" }}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                <Bot size={11} className="text-white" />
              </div>
              <span className="text-xs font-semibold text-blue-400">FikirLab Asistanı</span>
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
                    <Bot size={11} className="text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-primary text-white rounded-tr-sm"
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
                  onClick={onAnalyze}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-blue-600 text-white text-sm font-semibold rounded-xl transition-all"
                  style={{ animation: "step-appear 0.4s ease-out" }}
                >
                  <Sparkles size={14} />Fikri Analiz Et<ArrowRight size={13} />
                </button>
              </div>
            )}
          </div>
          <div ref={endRef} />
        </div>

        {/* Suggestion chips */}
        {msgs.length === 0 && (
          <div className="px-5 pb-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => setInput(s)}
                className="text-left text-xs px-3.5 py-2.5 rounded-xl border border-border bg-muted text-muted-foreground hover:text-foreground hover:border-blue-500/40 hover:bg-secondary transition-all leading-relaxed"
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
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
              placeholder="İş fikrinizi birkaç cümleyle anlatın..."
              rows={2}
              className="flex-1 bg-muted border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 resize-none transition-all"
            />
            <button
              onClick={() => send()}
              disabled={!input.trim()}
              className="w-11 h-11 bg-primary hover:bg-blue-600 text-white rounded-xl flex items-center justify-center transition-all disabled:opacity-40 flex-shrink-0"
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
