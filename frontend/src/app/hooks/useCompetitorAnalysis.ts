import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateCompetitorAnalysis,
  getCompetitorAnalysis,
  type CompetitorAnalysisData,
} from "../lib/api";

export type CompetitorAnalysisStatus = "loading" | "empty" | "ready" | "generating" | "error";

export function useCompetitorAnalysis(ideaId: number) {
  const [status, setStatus] = useState<CompetitorAnalysisStatus>("loading");
  const [data, setData] = useState<CompetitorAnalysisData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getCompetitorAnalysis(ideaId);
      setData(res.analysis_data);
      setStatus("ready");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setData(null);
        setStatus("empty");
      } else {
        setError(err instanceof ApiError ? err.message : "Rakip analizi yüklenemedi.");
        setStatus("error");
      }
    }
  }, [ideaId]);

  useEffect(() => {
    load();
  }, [load]);

  const generate = useCallback(async () => {
    setStatus("generating");
    setError(null);

    try {
      const res = await generateCompetitorAnalysis(ideaId);
      setData(res.analysis_data);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Rakip analizi oluşturulamadı.");
      setStatus("error");
    }
  }, [ideaId]);

  return { status, data, error, reload: load, generate };
}
