import { useEffect, useState } from "react";

const STORAGE_KEY = "fikirlab_active_idea_id";
const DEFAULT_IDEA_ID = 1;

function readStoredIdeaId(): number {
  const raw = localStorage.getItem(STORAGE_KEY);
  const parsed = raw ? Number(raw) : NaN;
  return Number.isFinite(parsed) && parsed > 0 ? parsed : DEFAULT_IDEA_ID;
}

export function useActiveIdeaId() {
  const [ideaId, setIdeaIdState] = useState<number>(readStoredIdeaId);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(ideaId));
  }, [ideaId]);

  const setIdeaId = (value: number) => {
    if (Number.isFinite(value) && value > 0) setIdeaIdState(value);
  };

  return [ideaId, setIdeaId] as const;
}
