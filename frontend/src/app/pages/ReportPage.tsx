import { useEffect, useRef, useState } from "react";
import { LayoutDashboard, Bot, BarChart3, FileText, History, Settings, ChevronRight, AlertTriangle, CheckCircle, Clock, Users, Target, MessageSquare, RefreshCw, Download, Send, Sparkles, TrendingUp, Calendar, Tag, Map, HelpCircle, Zap, Star, Menu, X, ArrowRight, Plus } from "lucide-react";
import { analysisData, initialMessages, sampleIdeas } from "../data/mockData";
import type { ChatMessage } from "../types";
import { RiskBadge, StatusBadge } from "../components/common/Badges";
import { MentorCharacter } from "../components/mentor/MentorCharacter";

export function ReportPage({ onBack }: { onBack: () => void }) {
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
            <h1 className="text-2xl font-bold text-foreground">Restoran Stok Yönetim Uygulaması</h1>
            <p className="text-sm text-muted-foreground mt-1">28 Haziran 2025 tarihli analiz</p>
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
            <p className="text-sm text-muted-foreground leading-relaxed">{analysisData.summary}</p>
          </section>

          <section>
            <Divider label="Problem ve Hedef Kitle" />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-card rounded-xl border border-border p-5">
                <h3 className="text-sm font-bold text-foreground mb-2">Problem</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Küçük restoranların manuel stok yönetimi nedeniyle günlük %8–15 oranında gıda israfı ve yükselen operasyonel maliyet.
                </p>
              </div>
              <div className="bg-card rounded-xl border border-border p-5">
                <h3 className="text-sm font-bold text-foreground mb-2">Hedef Kitle</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Günlük 50–300 müşteriye hizmet veren, teknolojiye açık küçük ve orta ölçekli restoran sahipleri ve şefleri.
                </p>
              </div>
            </div>
          </section>

          <section>
            <Divider label="Riskli Varsayımlar" />
            <div className="space-y-2.5">
              {analysisData.risks.map((r) => (
                <div key={r.id} className="flex items-start gap-3 bg-card rounded-xl border border-border p-4">
                  <RiskBadge level={r.level} />
                  <p className="text-sm text-muted-foreground">{r.text}</p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <Divider label="Müşteri Görüşme Soruları" />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {analysisData.questions.map((q, i) => (
                <div key={i} className="bg-card rounded-xl border border-border p-4">
                  <span className="text-xs font-bold text-blue-400 mb-1.5 block">Soru {i + 1}</span>
                  <p className="text-sm text-muted-foreground">{q}</p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <Divider label="MVP Kapsamı (MoSCoW)" />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                { key: "mustHave",   label: "Must Have",   bg: "bg-red-900/20 border-red-800/30",   lc: "text-red-400" },
                { key: "shouldHave", label: "Should Have", bg: "bg-amber-900/20 border-amber-800/30", lc: "text-amber-400" },
                { key: "couldHave",  label: "Could Have",  bg: "bg-blue-900/20 border-blue-800/30",  lc: "text-blue-400" },
                { key: "wontHave",   label: "Won't Have",  bg: "bg-slate-800/30 border-slate-700/30", lc: "text-slate-400" },
              ].map(({ key, label, bg, lc }) => (
                <div key={key} className={`rounded-xl border p-4 ${bg}`}>
                  <div className={`text-xs font-bold mb-2 ${lc}`}>{label}</div>
                  <ul className="space-y-1">
                    {(analysisData.mvp as any)[key].map((item: string, i: number) => (
                      <li key={i} className={`text-xs ${lc} opacity-70`}>· {item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>

          <section>
            <Divider label="Doğrulama Yol Haritası" />
            {analysisData.roadmap.map((item, i) => (
              <div key={item.step} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-primary text-white text-sm font-bold flex items-center justify-center flex-shrink-0">{item.step}</div>
                  {i < analysisData.roadmap.length - 1 && <div className="w-px flex-1 bg-border my-1" style={{ minHeight: 24 }} />}
                </div>
                <div className={`flex-1 ${i < analysisData.roadmap.length - 1 ? "pb-5" : ""}`}>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-foreground">{item.title}</span>
                    <span className="text-xs text-muted-foreground">{item.weeks}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </section>

          <section>
            <Divider label="Sonraki Adımlar" />
            <div className="bg-blue-900/20 border border-blue-800/30 rounded-xl p-5">
              <div className="flex items-center gap-1.5 mb-2">
                <Zap size={13} className="text-blue-400" />
                <span className="text-sm font-bold text-blue-300">İlk Aksiyon</span>
              </div>
              <p className="text-sm text-blue-300/80 leading-relaxed">{analysisData.evaluation.nextAction}</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
