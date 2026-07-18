import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, HelpCircle, Zap, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { analysisData, initialMessages, sampleIdeas } from "../data/mockData";
import type { ChatMessage } from "../types";
import { RiskBadge, StatusBadge } from "../components/common/Badges";
import { MentorCharacter } from "../components/mentor/MentorCharacter";

export function LoadingPage({ onDone }: { onDone: () => void }) {
  const [step, setStep] = useState(0);
  const steps = [
    "Fikir özeti çıkarılıyor",
    "Riskli varsayımlar belirleniyor",
    "Müşteri soruları hazırlanıyor",
    "MVP kapsamı oluşturuluyor",
    "Yol haritası hazırlanıyor",
  ];

  useEffect(() => {
    const t = setInterval(() => setStep((p) => { if (p >= steps.length - 1) { clearInterval(t); return p; } return p + 1; }), 1200);
    return () => clearInterval(t);
  }, []);

  useEffect(() => { if (step === steps.length - 1) { const t = setTimeout(onDone, 1300); return () => clearTimeout(t); } }, [step]);

  return (
    <div className="flex-1 flex items-center justify-center" style={{ animation: "page-in 0.3s ease-out" }}>
      <div className="text-center max-w-sm px-6">
        <div className="w-16 h-16 rounded-2xl bg-primary/15 border border-primary/20 flex items-center justify-center mx-auto mb-7">
          <Sparkles size={26} className="text-blue-400 animate-pulse" />
        </div>
        <h1 className="text-xl font-bold text-foreground">Fikrin analiz ediliyor</h1>
        <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
          AI; riskli varsayımları, müşteri sorularını, MVP kapsamını ve doğrulama yol haritanı hazırlıyor.
        </p>
        <div className="mt-8 space-y-3 text-left">
          {steps.map((s, i) => (
            <div
              key={s}
              className={`flex items-center gap-3 transition-all duration-500 ${i > step ? "opacity-25" : "opacity-100"}`}
              style={i <= step ? { animation: `step-appear 0.4s ease-out` } : {}}
            >
              <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-500 ${
                i < step ? "bg-emerald-500" : i === step ? "bg-primary" : "bg-border"
              }`}>
                {i < step && <CheckCircle size={11} className="text-white" />}
                {i === step && <div className="w-2 h-2 rounded-full bg-white animate-pulse" />}
              </div>
              <span className={`text-sm ${i <= step ? "text-foreground font-medium" : "text-muted-foreground"}`}>{s}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
