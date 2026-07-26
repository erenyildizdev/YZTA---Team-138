import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateRiskyAssumptions,
  getRiskyAssumptions,
  type RiskyAssumptionsData,
} from "../lib/api";

export type RiskyAssumptionsStatus = "loading" | "empty" | "ready" | "generating" | "error";

export function useRiskyAssumptions(ideaId: number) {
  const [status, setStatus] = useState<RiskyAssumptionsStatus>("loading");
  const [data, setData] = useState<RiskyAssumptionsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getRiskyAssumptions(ideaId);
      setData(res.assumptions_data);
      setStatus("ready");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setData(null);
        setStatus("empty");
      } else {
        setError(err instanceof ApiError ? err.message : "Riskli varsayımlar yüklenemedi.");
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
      const res = await generateRiskyAssumptions(ideaId);
      setData(res.assumptions_data);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Riskli varsayımlar oluşturulamadı.");
      setStatus("error");
    }
  }, [ideaId]);

  return { status, data, error, reload: load, generate };
}
