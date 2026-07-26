import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, HelpCircle, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { initialMessages, sampleIdeas } from "../data/mockData";
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

export function ReportPage({ onBack }: { onBack: () => void }) {
  const [ideaId] = useActiveIdeaId();
  const { data: idea } = useIdea(ideaId);
  const Divider = ({ label }: { label: string }) => (
    <div className="flex items-center gap-2 mb-4">
      <div className="w-4 h-0.5 bg-primary rounded-full" />
      <h2 className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">{label}</h2>
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto hide-scroll" style={{ animation: "page-in 0.3s ease-out" }}>
      <div className="max-w-3xl mx-auto px-4 sm:px-7 py-7 sm:py-10">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-10">
          <div>
            <div className="text-xs text-muted-foreground mb-1 tracking-widest uppercase">FikirLab — Doğrulama Raporu</div>
            <h1 className="text-2xl font-bold text-foreground">{idea?.title ?? "Yükleniyor..."}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              {idea ? `${new Date(idea.created_at).toLocaleDateString("tr-TR")} tarihli analiz` : ""}
            </p>
          </div>
          <button
            disabled
            title="Backend entegrasyonu sonrasında kullanılabilir"
            className="inline-flex cursor-not-allowed items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-semibold bg-primary text-white opacity-45"
          >
            <Download size={14} />PDF İndir
          </button>
        </div>

        <button type="button" onClick={onBack} className="mb-6 text-xs font-semibold text-blue-400 hover:text-blue-300">
          ← Fikir analizine dön
        </button>

        <div className="space-y-9">
          <section>
            <Divider label="Fikir Özeti" />
            <p className="text-sm text-muted-foreground leading-relaxed">{idea?.description}</p>
          </section>

          <section>
            <Divider label="Problem ve Hedef Kitle" />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-card rounded-xl border border-border p-5">
                <h3 className="text-sm font-bold text-foreground mb-2">Problem</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{idea?.problem}</p>
              </div>
              <div className="bg-card rounded-xl border border-border p-5">
                <h3 className="text-sm font-bold text-foreground mb-2">Hedef Kitle</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{idea?.target_audience}</p>
              </div>
            </div>
          </section>

          <section>
            <Divider label="Riskli Varsayımlar" />
            <RiskyAssumptionsBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="Müşteri Görüşme Soruları" />
            <MomTestQuestionsBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="MVP Kapsamı (MoSCoW)" />
            <MoscowScopeBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="Doğrulama Yol Haritası" />
            <ValidationRoadmapBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="Genel Değerlendirme" />
            <GeneralEvaluationBody ideaId={ideaId} />
          </section>
        </div>
      </div>
    </div>
  );
}
