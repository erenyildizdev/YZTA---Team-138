import { useCallback, useEffect, useState } from "react";
import { ApiError, getIdea, type IdeaResponse } from "../lib/api";

export type IdeaFetchStatus = "loading" | "ready" | "error";

export function useIdea(ideaId: number) {
  const [status, setStatus] = useState<IdeaFetchStatus>("loading");
  const [data, setData] = useState<IdeaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getIdea(ideaId);
      setData(res);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Fikir yüklenemedi.");
      setStatus("error");
    }
  }, [ideaId]);

  useEffect(() => {
    load();
  }, [load]);

  return { status, data, error, reload: load };
}
