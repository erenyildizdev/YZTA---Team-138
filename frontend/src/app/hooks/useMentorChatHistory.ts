import { useCallback, useEffect, useState } from "react";

export interface MentorChatMessage {
  role: "user" | "ai";
  text: string;
}

const STORAGE_PREFIX = "fikirlab_mentor_chat_";
const MAX_STORED_MESSAGES = 50;

function storageKey(ideaId: number) {
  return `${STORAGE_PREFIX}${ideaId}`;
}

function readStored(ideaId: number): MentorChatMessage[] {
  try {
    const raw = localStorage.getItem(storageKey(ideaId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

type MsgUpdater = MentorChatMessage[] | ((prev: MentorChatMessage[]) => MentorChatMessage[]);

export function useMentorChatHistory(ideaId: number) {
  const [msgs, setMsgsState] = useState<MentorChatMessage[]>(() => readStored(ideaId));

  useEffect(() => {
    setMsgsState(readStored(ideaId));
  }, [ideaId]);

  const setMsgs = useCallback(
    (updater: MsgUpdater) => {
      setMsgsState((prev) => {
        const next = typeof updater === "function" ? updater(prev) : updater;
        const trimmed = next.slice(-MAX_STORED_MESSAGES);
        try {
          localStorage.setItem(storageKey(ideaId), JSON.stringify(trimmed));
        } catch {
          // ignore storage quota errors
        }
        return trimmed;
      });
    },
    [ideaId],
  );

  return [msgs, setMsgs] as const;
}
