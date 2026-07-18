import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, HelpCircle, Zap, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { analysisData, initialMessages, sampleIdeas } from "../data/mockData";
import type { ChatMessage } from "../types";
import { RiskBadge, StatusBadge } from "../components/common/Badges";
import { MentorCharacter } from "../components/mentor/MentorCharacter";

export function HistoryPage({ onOpen }: { onOpen: () => void }) {
  return (
    <div className="flex-1 overflow-y-auto hide-scroll" style={{ animation: "page-in 0.3s ease-out" }}>
      <div className="max-w-4xl mx-auto px-4 sm:px-7 py-7 sm:py-10">
        <div className="mb-7">
          <h1 className="text-xl font-bold text-foreground">Geçmiş Fikirler</h1>
          <p className="text-sm text-muted-foreground mt-1">Daha önce oluşturduğunuz tüm fikirler ve analiz durumları.</p>
        </div>
        <div className="grid gap-4">
          {sampleIdeas.map((idea) => (
            <div key={idea.id} className="bg-card rounded-xl border border-border p-5 hover:border-blue-500/30 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2.5">
                    <StatusBadge status={idea.status} />
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Calendar size={10} />{idea.date}
                    </span>
                  </div>
                  <h3 className="font-semibold text-foreground">{idea.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{idea.description}</p>
                  <div className="flex items-center gap-3 mt-3">
                    <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                      <Tag size={10} />{idea.sector}
                    </span>
                    <span className="text-border text-xs">·</span>
                    <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                      <Users size={10} />{idea.targetAudience}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => idea.status === "complete" && onOpen()}
                  disabled={idea.status === "draft"}
                  className="flex-shrink-0 inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-border text-muted-foreground hover:text-foreground hover:border-blue-500/40 hover:bg-secondary transition-all disabled:opacity-35 disabled:cursor-not-allowed"
                >
                  Detaya Git<ChevronRight size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
