import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, HelpCircle, Zap, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { analysisData, initialMessages, sampleIdeas } from "../data/mockData";
import type { ChatMessage } from "../types";
import { RiskBadge, StatusBadge } from "../components/common/Badges";
import { MentorCharacter } from "../components/mentor/MentorCharacter";

export function DashboardPage({
  onNew, onViewAll, onOpenDetail,
}: {
  onNew: () => void;
  onViewAll: () => void;
  onOpenDetail: () => void;
}) {
  const stats = [
    { label: "Toplam Fikir",   value: "3", Icon: Sparkles,   accent: "text-blue-400",    bg: "bg-blue-500/10",    border: "border-blue-500/20" },
    { label: "Analiz Edildi",  value: "2", Icon: BarChart3,   accent: "text-violet-400",  bg: "bg-violet-500/10",  border: "border-violet-500/20" },
    { label: "Devam Eden",     value: "1", Icon: TrendingUp,  accent: "text-amber-400",   bg: "bg-amber-500/10",   border: "border-amber-500/20" },
  ];

  return (
    <div className="flex-1 overflow-y-auto hide-scroll" style={{ animation: "page-in 0.3s ease-out" }}>
      <div className="max-w-4xl mx-auto px-4 sm:px-7 py-7 sm:py-10">
        <div className="mb-10">
          <h1 className="text-2xl font-bold text-foreground tracking-tight">
            Fikirlerini doğrulamaya hazır mısın? 👋
          </h1>
          <p className="text-sm text-muted-foreground mt-2 leading-relaxed max-w-lg">
            AI destekli analizlerle iş fikirlerindeki riskleri keşfet, müşteri görüşme sorularını oluştur ve MVP kapsamını daralt.
          </p>
          <button
            onClick={onNew}
            className="mt-5 inline-flex items-center gap-2 bg-primary hover:bg-blue-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-all"
          >
            <Plus size={15} />Yeni Fikir Oluştur
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          {stats.map((s) => (
            <div key={s.label} className={`bg-card rounded-xl p-5 border ${s.border}`}>
              <div className={`w-9 h-9 rounded-xl ${s.bg} flex items-center justify-center mb-3 border ${s.border}`}>
                <s.Icon size={17} className={s.accent} />
              </div>
              <div className={`text-2xl font-bold ${s.accent}`}>{s.value}</div>
              <div className="text-sm text-muted-foreground mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Recent ideas */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-foreground">Son Fikirler</h2>
            <button onClick={onViewAll} className="text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors">
              Tümünü Gör
            </button>
          </div>
          <div className="space-y-3">
            {sampleIdeas.map((idea) => (
              <div
                key={idea.id}
                className="bg-card rounded-xl p-5 border border-border hover:border-blue-500/30 transition-all group"
              >
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <StatusBadge status={idea.status} />
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Calendar size={10} />{idea.date}
                      </span>
                    </div>
                    <h3 className="font-semibold text-foreground text-sm">{idea.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1 leading-relaxed line-clamp-1">{idea.description}</p>
                    <div className="flex items-center gap-3 mt-2.5">
                      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                        <Tag size={10} />{idea.sector}
                      </span>
                      <span className="text-border">·</span>
                      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                        <Users size={10} />{idea.targetAudience}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => idea.status === "complete" && onOpenDetail()}
                    disabled={idea.status === "draft"}
                    className="flex-shrink-0 inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-secondary text-muted-foreground hover:bg-primary/20 hover:text-blue-400 border border-border hover:border-blue-500/40 transition-all disabled:opacity-35 disabled:cursor-not-allowed"
                  >
                    Detaya Git<ChevronRight size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
