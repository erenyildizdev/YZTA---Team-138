import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateMomTestQuestions,
  type MomTestQuestionItem,
} from "../lib/api";

export type MomTestQuestionsStatus = "generating" | "ready" | "error";

export function useMomTestQuestions(ideaId: number) {
  const [status, setStatus] = useState<MomTestQuestionsStatus>("generating");
  const [data, setData] = useState<MomTestQuestionItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

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
    generate();
  }, [generate]);

  return { status, data, error, generate };
}
