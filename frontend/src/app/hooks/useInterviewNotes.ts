import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiError,
  createInterviewNote,
  deleteInterviewNote,
  getInterviewNotes,
  updateInterviewNote,
  type InterviewNotePayload,
  type InterviewNoteResponse,
  type InterviewNoteUpdatePayload,
} from "../lib/api";

export type InterviewNotesStatus = "loading" | "ready" | "error";

interface InterviewNotesState {
  ideaId: number;
  status: InterviewNotesStatus;
  notes: InterviewNoteResponse[];
  loadError: string | null;
  isCreating: boolean;
  createError: string | null;
  updatingNoteIds: number[];
  updateErrors: Record<number, string>;
  deletingNoteIds: number[];
  deleteErrors: Record<number, string>;
}

type MutationAction = "create" | "update" | "delete";

interface MutationLock {
  token: symbol;
  ideaId: number;
  action: MutationAction;
  noteId?: number;
}

interface ListRequest {
  token: symbol;
  revision: number;
}

interface PendingMutationState {
  isCreating: boolean;
  updatingNoteIds: number[];
  deletingNoteIds: number[];
}

function initialState(ideaId: number): InterviewNotesState {
  return {
    ideaId,
    status: "loading",
    notes: [],
    loadError: null,
    isCreating: false,
    createError: null,
    updatingNoteIds: [],
    updateErrors: {},
    deletingNoteIds: [],
    deleteErrors: {},
  };
}

function withoutError(
  errors: Record<number, string>,
  noteId: number,
): Record<number, string> {
  const nextErrors = { ...errors };
  delete nextErrors[noteId];
  return nextErrors;
}

function loadErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Oturumun doğrulanamadı. Lütfen yeniden giriş yapıp tekrar dene.";
    }
    if (error.status === 403) {
      return "Bu fikrin görüşme notlarını görüntüleme yetkin bulunmuyor.";
    }
    if (error.status === 404) {
      return "Fikir bulunamadı veya görüşme notlarına erişilemiyor.";
    }
  }

  return "Görüşme notları yüklenemedi. Lütfen bağlantını kontrol edip tekrar dene.";
}

function mutationErrorMessage(error: unknown, action: MutationAction): string {
  const fallback = {
    create: "Görüşme notu kaydedilemedi. Lütfen tekrar dene.",
    update: "Görüşme notu güncellenemedi. Lütfen tekrar dene.",
    delete: "Görüşme notu silinemedi. Lütfen tekrar dene.",
  }[action];

  if (!(error instanceof ApiError)) {
    return fallback;
  }

  if (error.status === 400) {
    return action === "delete"
      ? fallback
      : "Girdiğin bilgileri kontrol edip tekrar dene.";
  }
  if (error.status === 401) {
    return "Oturumun doğrulanamadı. Lütfen yeniden giriş yapıp tekrar dene.";
  }
  if (error.status === 403) {
    return "Bu işlem için yetkin bulunmuyor.";
  }
  if (error.status === 404) {
    return action === "create"
      ? "Fikir bulunamadı veya bu fikre not ekleme yetkin bulunmuyor."
      : "Görüşme notu bulunamadı veya bu nota erişilemiyor.";
  }

  return fallback;
}

function isUncertainMutationError(error: unknown): boolean {
  return !(error instanceof ApiError) || error.status >= 500;
}

function createMutationKey(ideaId: number): string {
  return `create:${ideaId}`;
}

function noteMutationKey(ideaId: number, noteId: number): string {
  return `note:${ideaId}:${noteId}`;
}

function pendingMutationState(
  locks: Map<string, MutationLock>,
  ideaId: number,
): PendingMutationState {
  const pending: PendingMutationState = {
    isCreating: false,
    updatingNoteIds: [],
    deletingNoteIds: [],
  };

  locks.forEach((lock) => {
    if (lock.ideaId !== ideaId) {
      return;
    }

    if (lock.action === "create") {
      pending.isCreating = true;
    } else if (lock.action === "update" && lock.noteId !== undefined) {
      pending.updatingNoteIds.push(lock.noteId);
    } else if (lock.action === "delete" && lock.noteId !== undefined) {
      pending.deletingNoteIds.push(lock.noteId);
    }
  });

  return pending;
}

function isInterviewNoteResponse(
  value: unknown,
  ideaId: number,
  noteId?: number,
): value is InterviewNoteResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const note = value as Record<string, unknown>;
  return (
    typeof note.id === "number" &&
    (noteId === undefined || note.id === noteId) &&
    note.idea_id === ideaId &&
    typeof note.interviewee_name === "string" &&
    typeof note.interviewee_profile === "string" &&
    typeof note.notes === "string" &&
    (note.interviewed_at === null ||
      typeof note.interviewed_at === "string") &&
    typeof note.created_at === "string" &&
    typeof note.updated_at === "string"
  );
}

function requireInterviewNote(
  value: unknown,
  ideaId: number,
  noteId?: number,
): InterviewNoteResponse {
  if (!isInterviewNoteResponse(value, ideaId, noteId)) {
    throw new Error("Görüşme notu yanıtı beklenen formatta değil.");
  }
  return value;
}

function requireInterviewNotes(
  value: unknown,
  ideaId: number,
): InterviewNoteResponse[] {
  if (
    !Array.isArray(value) ||
    !value.every((note) => isInterviewNoteResponse(note, ideaId))
  ) {
    throw new Error("Görüşme notları yanıtı beklenen formatta değil.");
  }
  return value;
}

export function useInterviewNotes(ideaId: number, refreshToken = 0) {
  const [state, setState] = useState<InterviewNotesState>(() => initialState(ideaId));
  const mountedRef = useRef(true);
  const currentIdeaIdRef = useRef(ideaId);
  const ideaGenerationRef = useRef(0);
  const loadedIdeaIdRef = useRef<number | null>(null);
  const mutationLocksRef = useRef<Map<string, MutationLock>>(new Map());
  const revisionCountersRef = useRef<Map<number, number>>(new Map());
  const dirtyRevisionsRef = useRef<Map<number, number>>(new Map());
  const lastAttemptedRevisionsRef = useRef<Map<number, number>>(new Map());
  const listRequestsRef = useRef<Map<number, ListRequest>>(new Map());
  const ensureReconciliationRef = useRef<(requestedIdeaId: number) => void>(
    () => undefined,
  );
  const previousRefreshTokenRef = useRef(refreshToken);

  useEffect(() => {
    currentIdeaIdRef.current = ideaId;
    if (loadedIdeaIdRef.current !== ideaId) {
      loadedIdeaIdRef.current = null;
    }
    ideaGenerationRef.current += 1;

    return () => {
      ideaGenerationRef.current += 1;
    };
  }, [ideaId]);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
    };
  }, []);

  const isCurrentRequest = useCallback(
    (requestedIdeaId: number, generation: number) =>
      mountedRef.current &&
      currentIdeaIdRef.current === requestedIdeaId &&
      ideaGenerationRef.current === generation,
    [],
  );

  const hasActiveMutationForIdea = useCallback(
    (requestedIdeaId: number): boolean => {
      for (const lock of mutationLocksRef.current.values()) {
        if (lock.ideaId === requestedIdeaId) {
          return true;
        }
      }
      return false;
    },
    [],
  );

  const markIdeaDirty = useCallback((requestedIdeaId: number): number => {
    const revision =
      (revisionCountersRef.current.get(requestedIdeaId) ?? 0) + 1;
    revisionCountersRef.current.set(requestedIdeaId, revision);
    dirtyRevisionsRef.current.set(requestedIdeaId, revision);
    return revision;
  }, []);

  const acquireMutationLock = useCallback(
    (
      key: string,
      details: Omit<MutationLock, "token">,
    ): symbol | null => {
      if (mutationLocksRef.current.has(key)) {
        return null;
      }

      const token = Symbol(key);
      mutationLocksRef.current.set(key, { token, ...details });

      if (
        listRequestsRef.current.has(details.ideaId) ||
        dirtyRevisionsRef.current.has(details.ideaId)
      ) {
        markIdeaDirty(details.ideaId);
      }

      return token;
    },
    [markIdeaDirty],
  );

  const releaseMutationLock = useCallback(
    (key: string, token: symbol): boolean => {
      if (mutationLocksRef.current.get(key)?.token !== token) {
        return false;
      }
      mutationLocksRef.current.delete(key);
      return true;
    },
    [],
  );

  const syncVisiblePendingState = useCallback((requestedIdeaId: number) => {
    if (
      !mountedRef.current ||
      currentIdeaIdRef.current !== requestedIdeaId
    ) {
      return;
    }

    const pending = pendingMutationState(
      mutationLocksRef.current,
      requestedIdeaId,
    );
    setState((previousState) => {
      const currentState =
        previousState.ideaId === requestedIdeaId
          ? previousState
          : initialState(requestedIdeaId);
      return { ...currentState, ...pending };
    });
  }, []);

  const runReconciliation = useCallback(
    async (
      requestedIdeaId: number,
      generation: number,
      revision: number,
      token: symbol,
    ) => {
      try {
        const notes = requireInterviewNotes(
          await getInterviewNotes(requestedIdeaId),
          requestedIdeaId,
        );
        const activeRequest = listRequestsRef.current.get(requestedIdeaId);
        const canApply =
          activeRequest?.token === token &&
          isCurrentRequest(requestedIdeaId, generation) &&
          revisionCountersRef.current.get(requestedIdeaId) === revision &&
          dirtyRevisionsRef.current.get(requestedIdeaId) === revision &&
          !hasActiveMutationForIdea(requestedIdeaId);

        if (!canApply) {
          return;
        }

        dirtyRevisionsRef.current.delete(requestedIdeaId);
        lastAttemptedRevisionsRef.current.delete(requestedIdeaId);
        loadedIdeaIdRef.current = requestedIdeaId;
        setState((previousState) =>
          previousState.ideaId === requestedIdeaId
            ? {
                ...previousState,
                status: "ready",
                notes,
                loadError: null,
              }
            : previousState,
        );
      } catch {
        const activeRequest = listRequestsRef.current.get(requestedIdeaId);
        const canReport =
          activeRequest?.token === token &&
          isCurrentRequest(requestedIdeaId, generation) &&
          revisionCountersRef.current.get(requestedIdeaId) === revision &&
          dirtyRevisionsRef.current.get(requestedIdeaId) === revision &&
          !hasActiveMutationForIdea(requestedIdeaId);

        if (canReport) {
          setState((previousState) => {
            if (
              previousState.ideaId !== requestedIdeaId ||
              previousState.status !== "loading"
            ) {
              return previousState;
            }

            const hasUsableList =
              loadedIdeaIdRef.current === requestedIdeaId ||
              previousState.notes.length > 0;
            return hasUsableList
              ? {
                  ...previousState,
                  status: "ready",
                  loadError: null,
                }
              : {
                  ...previousState,
                  status: "error",
                  loadError:
                    "Görüşme notlarının güncel listesi alınamadı. Lütfen tekrar dene.",
                };
          });
        }
        // Keep the dirty revision. A later invalidation or manual reload retries it.
      } finally {
        if (listRequestsRef.current.get(requestedIdeaId)?.token === token) {
          listRequestsRef.current.delete(requestedIdeaId);
        }

        const latestRevision =
          dirtyRevisionsRef.current.get(requestedIdeaId);
        if (
          latestRevision !== undefined &&
          latestRevision !== revision
        ) {
          ensureReconciliationRef.current(requestedIdeaId);
        }
      }
    },
    [hasActiveMutationForIdea, isCurrentRequest],
  );

  const ensureReconciliation = useCallback(
    (requestedIdeaId: number) => {
      const revision = dirtyRevisionsRef.current.get(requestedIdeaId);
      if (
        revision === undefined ||
        !mountedRef.current ||
        currentIdeaIdRef.current !== requestedIdeaId ||
        hasActiveMutationForIdea(requestedIdeaId) ||
        listRequestsRef.current.has(requestedIdeaId) ||
        lastAttemptedRevisionsRef.current.get(requestedIdeaId) === revision
      ) {
        return;
      }

      const token = Symbol(`reconcile:${requestedIdeaId}:${revision}`);
      const generation = ideaGenerationRef.current;
      lastAttemptedRevisionsRef.current.set(requestedIdeaId, revision);
      listRequestsRef.current.set(requestedIdeaId, {
        token,
        revision,
      });
      void runReconciliation(
        requestedIdeaId,
        generation,
        revision,
        token,
      );
    },
    [hasActiveMutationForIdea, runReconciliation],
  );
  ensureReconciliationRef.current = ensureReconciliation;

  const load = useCallback(async () => {
    const requestedIdeaId = ideaId;
    const generation = ideaGenerationRef.current;

    if (!isCurrentRequest(requestedIdeaId, generation)) {
      return;
    }

    const pending = pendingMutationState(
      mutationLocksRef.current,
      requestedIdeaId,
    );
    setState((previousState) => {
      const currentState =
        previousState.ideaId === requestedIdeaId
          ? previousState
          : initialState(requestedIdeaId);

      return {
        ...currentState,
        ...pending,
        status: "loading",
        loadError: null,
      };
    });

    if (
      listRequestsRef.current.has(requestedIdeaId) ||
      hasActiveMutationForIdea(requestedIdeaId)
    ) {
      markIdeaDirty(requestedIdeaId);
      ensureReconciliationRef.current(requestedIdeaId);
      return;
    }

    const revision =
      revisionCountersRef.current.get(requestedIdeaId) ?? 0;
    const token = Symbol(`load:${requestedIdeaId}:${revision}`);
    listRequestsRef.current.set(requestedIdeaId, {
      token,
      revision,
    });

    try {
      const notes = requireInterviewNotes(
        await getInterviewNotes(requestedIdeaId),
        requestedIdeaId,
      );
      const activeRequest = listRequestsRef.current.get(requestedIdeaId);
      const canApply =
        activeRequest?.token === token &&
        isCurrentRequest(requestedIdeaId, generation) &&
        (revisionCountersRef.current.get(requestedIdeaId) ?? 0) === revision &&
        !hasActiveMutationForIdea(requestedIdeaId);

      if (!canApply) {
        return;
      }

      if (dirtyRevisionsRef.current.get(requestedIdeaId) === revision) {
        dirtyRevisionsRef.current.delete(requestedIdeaId);
        lastAttemptedRevisionsRef.current.delete(requestedIdeaId);
      }
      loadedIdeaIdRef.current = requestedIdeaId;
      setState((previousState) =>
        previousState.ideaId === requestedIdeaId
          ? {
              ...previousState,
              status: "ready",
              notes,
              loadError: null,
            }
          : previousState,
      );
    } catch (error) {
      const activeRequest = listRequestsRef.current.get(requestedIdeaId);
      const canReport =
        activeRequest?.token === token &&
        isCurrentRequest(requestedIdeaId, generation) &&
        (revisionCountersRef.current.get(requestedIdeaId) ?? 0) === revision &&
        !hasActiveMutationForIdea(requestedIdeaId);

      if (!canReport) {
        return;
      }

      if (dirtyRevisionsRef.current.get(requestedIdeaId) === revision) {
        lastAttemptedRevisionsRef.current.set(requestedIdeaId, revision);
      }
      setState((previousState) =>
        previousState.ideaId === requestedIdeaId
          ? {
              ...previousState,
              status: "error",
              loadError: loadErrorMessage(error),
            }
          : previousState,
      );
    } finally {
      if (listRequestsRef.current.get(requestedIdeaId)?.token === token) {
        listRequestsRef.current.delete(requestedIdeaId);
      }
      ensureReconciliationRef.current(requestedIdeaId);
    }
  }, [
    hasActiveMutationForIdea,
    ideaId,
    isCurrentRequest,
    markIdeaDirty,
  ]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (previousRefreshTokenRef.current === refreshToken) {
      return;
    }

    previousRefreshTokenRef.current = refreshToken;
    markIdeaDirty(ideaId);
    ensureReconciliationRef.current(ideaId);
  }, [ideaId, markIdeaDirty, refreshToken]);

  const addNote = useCallback(
    async (payload: InterviewNotePayload): Promise<boolean> => {
      const requestedIdeaId = ideaId;
      const generation = ideaGenerationRef.current;
      const key = createMutationKey(requestedIdeaId);

      if (!isCurrentRequest(requestedIdeaId, generation)) {
        return false;
      }

      const lockToken = acquireMutationLock(key, {
        ideaId: requestedIdeaId,
        action: "create",
      });
      if (!lockToken) {
        return false;
      }

      setState((previousState) => {
        const currentState =
          previousState.ideaId === requestedIdeaId
            ? previousState
            : initialState(requestedIdeaId);

        return {
          ...currentState,
          isCreating: true,
          createError: null,
        };
      });

      try {
        const note = requireInterviewNote(
          await createInterviewNote(requestedIdeaId, payload),
          requestedIdeaId,
        );
        if (!isCurrentRequest(requestedIdeaId, generation)) {
          markIdeaDirty(requestedIdeaId);
          return false;
        }

        const needsReconciliation =
          loadedIdeaIdRef.current !== requestedIdeaId;
        setState((previousState) => {
          if (previousState.ideaId !== requestedIdeaId) {
            return previousState;
          }

          const noteAlreadyExists = previousState.notes.some(
            (existingNote) => existingNote.id === note.id,
          );

          return {
            ...previousState,
            status: "ready",
            loadError: null,
            createError: null,
            notes: noteAlreadyExists
              ? previousState.notes.map((existingNote) =>
                  existingNote.id === note.id ? note : existingNote,
                )
              : [note, ...previousState.notes],
          };
        });
        if (needsReconciliation) {
          markIdeaDirty(requestedIdeaId);
        }
        return true;
      } catch (error) {
        if (isUncertainMutationError(error)) {
          markIdeaDirty(requestedIdeaId);
        }

        if (isCurrentRequest(requestedIdeaId, generation)) {
          setState((previousState) =>
            previousState.ideaId === requestedIdeaId
              ? {
                  ...previousState,
                  createError: mutationErrorMessage(error, "create"),
                }
              : previousState,
          );
        }
        return false;
      } finally {
        if (releaseMutationLock(key, lockToken)) {
          syncVisiblePendingState(requestedIdeaId);
          ensureReconciliationRef.current(requestedIdeaId);
        }
      }
    },
    [
      acquireMutationLock,
      ideaId,
      isCurrentRequest,
      markIdeaDirty,
      releaseMutationLock,
      syncVisiblePendingState,
    ],
  );

  const updateNote = useCallback(
    async (
      noteId: number,
      payload: InterviewNoteUpdatePayload,
    ): Promise<boolean> => {
      const requestedIdeaId = ideaId;
      const generation = ideaGenerationRef.current;
      const key = noteMutationKey(requestedIdeaId, noteId);

      if (!isCurrentRequest(requestedIdeaId, generation)) {
        return false;
      }

      const lockToken = acquireMutationLock(key, {
        ideaId: requestedIdeaId,
        action: "update",
        noteId,
      });
      if (!lockToken) {
        return false;
      }

      setState((previousState) => {
        const currentState =
          previousState.ideaId === requestedIdeaId
            ? previousState
            : initialState(requestedIdeaId);

        return {
          ...currentState,
          updatingNoteIds: currentState.updatingNoteIds.includes(noteId)
            ? currentState.updatingNoteIds
            : [...currentState.updatingNoteIds, noteId],
          updateErrors: withoutError(currentState.updateErrors, noteId),
          deleteErrors: withoutError(currentState.deleteErrors, noteId),
        };
      });

      try {
        const updatedNote = requireInterviewNote(
          await updateInterviewNote(requestedIdeaId, noteId, payload),
          requestedIdeaId,
          noteId,
        );
        if (!isCurrentRequest(requestedIdeaId, generation)) {
          markIdeaDirty(requestedIdeaId);
          return false;
        }

        const needsReconciliation =
          loadedIdeaIdRef.current !== requestedIdeaId;
        setState((previousState) =>
          previousState.ideaId === requestedIdeaId
            ? {
                ...previousState,
                status: "ready",
                loadError: null,
                updateErrors: withoutError(previousState.updateErrors, noteId),
                notes: previousState.notes.map((note) =>
                  note.id === noteId ? updatedNote : note,
                ),
              }
            : previousState,
        );
        if (needsReconciliation) {
          markIdeaDirty(requestedIdeaId);
        }
        return true;
      } catch (error) {
        if (isUncertainMutationError(error)) {
          markIdeaDirty(requestedIdeaId);
        }

        if (isCurrentRequest(requestedIdeaId, generation)) {
          setState((previousState) =>
            previousState.ideaId === requestedIdeaId
              ? {
                  ...previousState,
                  updateErrors: {
                    ...previousState.updateErrors,
                    [noteId]: mutationErrorMessage(error, "update"),
                  },
                }
              : previousState,
          );
        }
        return false;
      } finally {
        if (releaseMutationLock(key, lockToken)) {
          syncVisiblePendingState(requestedIdeaId);
          ensureReconciliationRef.current(requestedIdeaId);
        }
      }
    },
    [
      acquireMutationLock,
      ideaId,
      isCurrentRequest,
      markIdeaDirty,
      releaseMutationLock,
      syncVisiblePendingState,
    ],
  );

  const deleteNote = useCallback(
    async (noteId: number): Promise<boolean> => {
      const requestedIdeaId = ideaId;
      const generation = ideaGenerationRef.current;
      const key = noteMutationKey(requestedIdeaId, noteId);

      if (!isCurrentRequest(requestedIdeaId, generation)) {
        return false;
      }

      const lockToken = acquireMutationLock(key, {
        ideaId: requestedIdeaId,
        action: "delete",
        noteId,
      });
      if (!lockToken) {
        return false;
      }

      setState((previousState) => {
        const currentState =
          previousState.ideaId === requestedIdeaId
            ? previousState
            : initialState(requestedIdeaId);

        return {
          ...currentState,
          deletingNoteIds: currentState.deletingNoteIds.includes(noteId)
            ? currentState.deletingNoteIds
            : [...currentState.deletingNoteIds, noteId],
          deleteErrors: withoutError(currentState.deleteErrors, noteId),
          updateErrors: withoutError(currentState.updateErrors, noteId),
        };
      });

      try {
        await deleteInterviewNote(requestedIdeaId, noteId);
        if (!isCurrentRequest(requestedIdeaId, generation)) {
          markIdeaDirty(requestedIdeaId);
          return false;
        }

        const needsReconciliation =
          loadedIdeaIdRef.current !== requestedIdeaId;
        setState((previousState) =>
          previousState.ideaId === requestedIdeaId
            ? {
                ...previousState,
                status: "ready",
                loadError: null,
                updateErrors: withoutError(previousState.updateErrors, noteId),
                deleteErrors: withoutError(previousState.deleteErrors, noteId),
                notes: previousState.notes.filter((note) => note.id !== noteId),
              }
            : previousState,
        );
        if (needsReconciliation) {
          markIdeaDirty(requestedIdeaId);
        }
        return true;
      } catch (error) {
        if (isUncertainMutationError(error)) {
          markIdeaDirty(requestedIdeaId);
        }

        if (isCurrentRequest(requestedIdeaId, generation)) {
          setState((previousState) =>
            previousState.ideaId === requestedIdeaId
              ? {
                  ...previousState,
                  deleteErrors: {
                    ...previousState.deleteErrors,
                    [noteId]: mutationErrorMessage(error, "delete"),
                  },
                }
              : previousState,
          );
        }
        return false;
      } finally {
        if (releaseMutationLock(key, lockToken)) {
          syncVisiblePendingState(requestedIdeaId);
          ensureReconciliationRef.current(requestedIdeaId);
        }
      }
    },
    [
      acquireMutationLock,
      ideaId,
      isCurrentRequest,
      markIdeaDirty,
      releaseMutationLock,
      syncVisiblePendingState,
    ],
  );

  const clearCreateError = useCallback(() => {
    setState((previousState) =>
      previousState.ideaId === ideaId
        ? { ...previousState, createError: null }
        : previousState,
    );
  }, [ideaId]);

  const clearUpdateError = useCallback(
    (noteId: number) => {
      setState((previousState) =>
        previousState.ideaId === ideaId
          ? {
              ...previousState,
              updateErrors: withoutError(previousState.updateErrors, noteId),
            }
          : previousState,
      );
    },
    [ideaId],
  );

  const clearDeleteError = useCallback(
    (noteId: number) => {
      setState((previousState) =>
        previousState.ideaId === ideaId
          ? {
              ...previousState,
              deleteErrors: withoutError(previousState.deleteErrors, noteId),
            }
          : previousState,
      );
    },
    [ideaId],
  );

  const visiblePending = pendingMutationState(
    mutationLocksRef.current,
    ideaId,
  );
  const currentState = {
    ...(state.ideaId === ideaId ? state : initialState(ideaId)),
    ...visiblePending,
  };

  return {
    ...currentState,
    reload: load,
    refetch: load,
    addNote,
    updateNote,
    deleteNote,
    clearCreateError,
    clearUpdateError,
    clearDeleteError,
  };
}
