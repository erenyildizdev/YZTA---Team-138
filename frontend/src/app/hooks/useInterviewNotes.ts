import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  createInterviewNote,
  getInterviewNotes,
  type InterviewNotePayload,
  type InterviewNoteResponse,
} from "../lib/api";

export type InterviewNotesStatus = "loading" | "ready" | "error";

export function useInterviewNotes(ideaId: number) {
  const [status, setStatus] = useState<InterviewNotesStatus>("loading");
  const [notes, setNotes] = useState<InterviewNoteResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getInterviewNotes(ideaId);
      setNotes(res);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Görüşme notları yüklenemedi.");
      setStatus("error");
    }
  }, [ideaId]);

  useEffect(() => {
    load();
  }, [load]);

  const addNote = useCallback(
    async (payload: InterviewNotePayload) => {
      setIsSubmitting(true);
      setError(null);
      try {
        const note = await createInterviewNote(ideaId, payload);
        setNotes((prev) => [note, ...prev]);
        return true;
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Görüşme notu eklenemedi.");
        return false;
      } finally {
        setIsSubmitting(false);
      }
    },
    [ideaId],
  );

  return { status, notes, error, reload: load, addNote, isSubmitting };
}
