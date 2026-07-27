import { useCallback, useEffect, useState } from "react";

import { getIdeas, type IdeaResponse } from "../lib/api";

export type IdeasStatus = "loading" | "ready" | "error";

export function useIdeas() {
  const [status, setStatus] = useState<IdeasStatus>("loading");
  const [data, setData] = useState<IdeaResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      setData(await getIdeas());
      setStatus("ready");
    } catch {
      setData([]);
      setError("Fikir geçmişi yüklenemedi. Lütfen tekrar dene.");
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { status, data, error, reload: load };
}
