import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  generateValidationRoadmap,
  getValidationRoadmap,
  type ValidationRoadmapData,
} from "../lib/api";

export type RoadmapStatus = "loading" | "empty" | "ready" | "generating" | "error";

export function useValidationRoadmap(ideaId: number) {
  const [status, setStatus] = useState<RoadmapStatus>("loading");
  const [data, setData] = useState<ValidationRoadmapData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const res = await getValidationRoadmap(ideaId);
      setData(res.roadmap_data);
      setStatus("ready");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setData(null);
        setStatus("empty");
      } else {
        setError(err instanceof ApiError ? err.message : "Yol haritası yüklenemedi.");
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
      const res = await generateValidationRoadmap(ideaId);
      setData(res.roadmap_data);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Yol haritası oluşturulamadı.");
      setStatus("error");
    }
  }, [ideaId]);

  return { status, data, error, reload: load, generate };
}
