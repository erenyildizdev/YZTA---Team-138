import { RefreshCw } from "lucide-react";
import { useMomTestQuestions } from "../../hooks/useMomTestQuestions";

export function MomTestQuestionsBody({ ideaId }: { ideaId: number }) {
  const { status, data, error, generate } = useMomTestQuestions(ideaId);

  return (
    <div>
      {status === "generating" && (
        <div className="space-y-2.5">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-9 rounded-xl bg-muted/40 border border-border animate-pulse" />
          ))}
        </div>
      )}

      {status === "error" && (
        <div className="bg-red-900/10 border border-red-800/30 rounded-xl p-4">
          <p className="text-xs text-red-400 mb-2.5">{error}</p>
          <button
            onClick={generate}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-red-800/40 text-red-400 hover:bg-red-900/20 transition-all"
          >
            <RefreshCw size={12} />Tekrar Dene
          </button>
        </div>
      )}

      {status === "ready" && data && (
        <div>
          <div className="flex items-center justify-end mb-2.5">
            <button
              onClick={generate}
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              <RefreshCw size={11} />Yeniden Oluştur
            </button>
          </div>
          <div className="space-y-2.5">
            {data.map((q, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5 border border-blue-500/20">
                  {i + 1}
                </span>
                <p className="text-sm text-muted-foreground">{q.question}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
