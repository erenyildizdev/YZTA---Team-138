import { useSyncExternalStore } from "react";

export const ACTIVE_IDEA_STORAGE_KEY = "fikirlab_active_idea_id";

export type ActiveIdeaState = {
  ideaId: number | null;
  setActiveIdeaId: (ideaId: number) => void;
  clearActiveIdeaId: () => void;
};

type StoreListener = () => void;

const listeners = new Set<StoreListener>();
let activeIdeaIdSnapshot: number | null | undefined;

function isValidIdeaId(value: number): boolean {
  return Number.isSafeInteger(value) && value > 0;
}

function readStoredIdeaId(): number | null {
  if (typeof window === "undefined") return null;

  try {
    const raw = window.localStorage.getItem(ACTIVE_IDEA_STORAGE_KEY);
    if (raw === null) return null;

    const parsed = Number(raw);
    if (isValidIdeaId(parsed)) return parsed;

    window.localStorage.removeItem(ACTIVE_IDEA_STORAGE_KEY);
  } catch {
    // Storage may be unavailable; the in-memory store remains usable.
  }

  return null;
}

function getActiveIdeaIdSnapshot(): number | null {
  if (activeIdeaIdSnapshot === undefined) {
    activeIdeaIdSnapshot = readStoredIdeaId();
  }

  return activeIdeaIdSnapshot;
}

function notifyListeners(): void {
  listeners.forEach((listener) => listener());
}

function updateSnapshot(ideaId: number | null): void {
  const changed = getActiveIdeaIdSnapshot() !== ideaId;
  activeIdeaIdSnapshot = ideaId;

  if (typeof window !== "undefined") {
    try {
      if (ideaId === null) {
        window.localStorage.removeItem(ACTIVE_IDEA_STORAGE_KEY);
      } else {
        window.localStorage.setItem(ACTIVE_IDEA_STORAGE_KEY, String(ideaId));
      }
    } catch {
      // Storage may be unavailable; subscribers still receive the in-memory state.
    }
  }

  if (changed) notifyListeners();
}

function handleStorageChange(event: StorageEvent): void {
  if (event.key !== ACTIVE_IDEA_STORAGE_KEY && event.key !== null) return;

  const storedIdeaId = readStoredIdeaId();
  if (getActiveIdeaIdSnapshot() === storedIdeaId) return;

  activeIdeaIdSnapshot = storedIdeaId;
  notifyListeners();
}

function subscribe(listener: StoreListener): () => void {
  const isFirstSubscriber = listeners.size === 0;
  listeners.add(listener);

  if (isFirstSubscriber && typeof window !== "undefined") {
    window.addEventListener("storage", handleStorageChange);

    const storedIdeaId = readStoredIdeaId();
    if (getActiveIdeaIdSnapshot() !== storedIdeaId) {
      activeIdeaIdSnapshot = storedIdeaId;
    }
  }

  return () => {
    listeners.delete(listener);
    if (listeners.size === 0 && typeof window !== "undefined") {
      window.removeEventListener("storage", handleStorageChange);
    }
  };
}

export function setActiveIdeaId(ideaId: number): void {
  if (!isValidIdeaId(ideaId)) return;
  updateSnapshot(ideaId);
}

export function clearActiveIdeaId(): void {
  updateSnapshot(null);
}

export function clearActiveIdeaIdIfMatches(ideaId: number): void {
  if (!isValidIdeaId(ideaId) || getActiveIdeaIdSnapshot() !== ideaId) return;
  updateSnapshot(null);
}

export function useActiveIdeaId(): ActiveIdeaState {
  const ideaId = useSyncExternalStore(
    subscribe,
    getActiveIdeaIdSnapshot,
    (): number | null => null,
  );

  return { ideaId, setActiveIdeaId, clearActiveIdeaId };
}
