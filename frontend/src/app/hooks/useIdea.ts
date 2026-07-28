import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, getIdea, type IdeaResponse } from "../lib/api";
import { clearActiveIdeaIdIfMatches } from "./useActiveIdeaId";

export type IdeaFetchStatus = "idle" | "loading" | "ready" | "not_found" | "error";

interface IdeaFetchState {
  ideaId: number | null;
  status: IdeaFetchStatus;
  data: IdeaResponse | null;
  error: string | null;
}

function initialState(ideaId: number | null): IdeaFetchState {
  return {
    ideaId,
    status: ideaId === null ? "idle" : "loading",
    data: null,
    error: null,
  };
}

export function useIdea(ideaId: number | null) {
  const [state, setState] = useState<IdeaFetchState>(() => initialState(ideaId));
  const requestSequence = useRef(0);
  const currentIdeaId = useRef(ideaId);
  currentIdeaId.current = ideaId;

  const load = useCallback(async () => {
    const requestedIdeaId = ideaId;

    if (requestedIdeaId !== currentIdeaId.current) {
      return;
    }

    const requestId = ++requestSequence.current;

    if (requestedIdeaId === null) {
      setState(initialState(null));
      return;
    }

    setState({
      ideaId: requestedIdeaId,
      status: "loading",
      data: null,
      error: null,
    });

    try {
      const res = await getIdea(requestedIdeaId);
      if (
        requestSequence.current !== requestId ||
        currentIdeaId.current !== requestedIdeaId
      ) {
        return;
      }

      setState({
        ideaId: requestedIdeaId,
        status: "ready",
        data: res,
        error: null,
      });
    } catch (err) {
      if (
        requestSequence.current !== requestId ||
        currentIdeaId.current !== requestedIdeaId
      ) {
        return;
      }

      if (err instanceof ApiError && err.status === 404) {
        setState({
          ideaId: requestedIdeaId,
          status: "not_found",
          data: null,
          error: null,
        });
        clearActiveIdeaIdIfMatches(requestedIdeaId);
        return;
      }

      setState({
        ideaId: requestedIdeaId,
        status: "error",
        data: null,
        error: err instanceof ApiError ? err.message : "Fikir yüklenemedi.",
      });
    }
  }, [ideaId]);

  useEffect(() => {
    void load();

    return () => {
      requestSequence.current += 1;
    };
  }, [load]);

  if (state.ideaId !== ideaId) {
    return {
      ...initialState(ideaId),
      reload: load,
    };
  }

  return { ...state, reload: load };
}
