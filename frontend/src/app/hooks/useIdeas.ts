import { useCallback, useEffect, useState } from "react";

import { deleteIdea, getIdeas, type IdeaResponse } from "../lib/api";

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

  const removeIdea = useCallback(async (ideaId: number) => {
    await deleteIdea(ideaId);
    setData((prev) => prev.filter((idea) => idea.id !== ideaId));
  }, []);

  return { status, data, error, reload: load, removeIdea };
}
