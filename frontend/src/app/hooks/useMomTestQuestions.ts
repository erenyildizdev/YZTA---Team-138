import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateMomTestQuestions,
  getMomTestQuestions,
  type MomTestQuestionItem,
} from "../lib/api";

export type MomTestQuestionsStatus = "loading" | "empty" | "generating" | "ready" | "error";

export function useMomTestQuestions(ideaId: number) {
  const [status, setStatus] = useState<MomTestQuestionsStatus>("loading");
  const [data, setData] = useState<MomTestQuestionItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);
    try {
      const res = await getMomTestQuestions(ideaId);
      setData(res.questions);
      setStatus("ready");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setData(null);
        setStatus("empty");
      } else {
        setError(err instanceof ApiError ? err.message : "Görüşme soruları yüklenemedi.");
        setStatus("error");
      }
    }
  }, [ideaId]);

  const generate = useCallback(async () => {
    setStatus("generating");
    setError(null);

    try {
      const res = await generateMomTestQuestions(ideaId);
      setData(res.questions);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Görüşme soruları oluşturulamadı.");
      setStatus("error");
    }
  }, [ideaId]);

  useEffect(() => {
    void load();
  }, [load]);

  return { status, data, error, generate, reload: load };
}
