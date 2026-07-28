import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateInvestorPitch,
  getInvestorPitch,
  type InvestorPitchData,
} from "../lib/api";

export type InvestorPitchStatus = "loading" | "empty" | "ready" | "generating" | "error";

export function useInvestorPitch(ideaId: number) {
  const [status, setStatus] = useState<InvestorPitchStatus>("loading");
  const [data, setData] = useState<InvestorPitchData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getInvestorPitch(ideaId);
      setData(res.pitch_data);
      setStatus("ready");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setData(null);
        setStatus("empty");
      } else {
        setError(err instanceof ApiError ? err.message : "Yatırımcı sunumu yüklenemedi.");
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
      const res = await generateInvestorPitch(ideaId);
      setData(res.pitch_data);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Yatırımcı sunumu oluşturulamadı.");
      setStatus("error");
    }
  }, [ideaId]);

  return { status, data, error, reload: load, generate };
}
