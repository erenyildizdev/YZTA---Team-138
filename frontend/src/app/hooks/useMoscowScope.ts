import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateMoscowScope,
  getMoscowScope,
  type MoscowScopeData,
} from "../lib/api";

export type MoscowScopeStatus = "loading" | "empty" | "ready" | "generating" | "error";

export function useMoscowScope(ideaId: number) {
  const [status, setStatus] = useState<MoscowScopeStatus>("loading");
  const [data, setData] = useState<MoscowScopeData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getMoscowScope(ideaId);
      setData(res);
      setStatus("ready");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setData(null);
        setStatus("empty");
      } else {
        setError(err instanceof ApiError ? err.message : "MVP kapsamı yüklenemedi.");
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
      const res = await generateMoscowScope(ideaId);
      setData(res);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "MVP kapsamı oluşturulamadı.");
      setStatus("error");
    }
  }, [ideaId]);

  return { status, data, error, reload: load, generate };
}
