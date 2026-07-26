import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateGeneralEvaluation,
  getGeneralEvaluation,
  type GeneralEvaluationData,
} from "../lib/api";

export type GeneralEvaluationStatus = "loading" | "empty" | "ready" | "generating" | "error";

export function useGeneralEvaluation(ideaId: number) {
  const [status, setStatus] = useState<GeneralEvaluationStatus>("loading");
  const [data, setData] = useState<GeneralEvaluationData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getGeneralEvaluation(ideaId);
      setData(res.evaluation_data);
      setStatus("ready");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setData(null);
        setStatus("empty");
      } else {
        setError(err instanceof ApiError ? err.message : "Genel değerlendirme yüklenemedi.");
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
      const res = await generateGeneralEvaluation(ideaId);
      setData(res.evaluation_data);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Genel değerlendirme oluşturulamadı.");
      setStatus("error");
    }
  }, [ideaId]);

  return { status, data, error, reload: load, generate };
}
