import { useCallback, useEffect, useRef, useState } from "react";

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

interface MentorChatState {
  ideaId: number | null;
  messages: MentorChatMessage[];
}

export function useMentorChatHistory(ideaId: number | null) {
  const [state, setState] = useState<MentorChatState>(() => ({
    ideaId,
    messages: ideaId === null ? [] : readStored(ideaId),
  }));
  const currentIdeaId = useRef(ideaId);
  currentIdeaId.current = ideaId;

  useEffect(() => {
    setState({
      ideaId,
      messages: ideaId === null ? [] : readStored(ideaId),
    });
  }, [ideaId]);

  const setMsgs = useCallback(
    (updater: MsgUpdater) => {
      if (currentIdeaId.current !== ideaId) {
        return;
      }

      if (ideaId === null) {
        setState({ ideaId: null, messages: [] });
        return;
      }

      setState((previousState) => {
        const previousMessages =
          previousState.ideaId === ideaId ? previousState.messages : readStored(ideaId);
        const next =
          typeof updater === "function" ? updater(previousMessages) : updater;
        const trimmed = next.slice(-MAX_STORED_MESSAGES);
        try {
          localStorage.setItem(storageKey(ideaId), JSON.stringify(trimmed));
        } catch {
          // ignore storage quota errors
        }
        return { ideaId, messages: trimmed };
      });
    },
    [ideaId],
  );

  const messages = state.ideaId === ideaId ? state.messages : [];
  return [messages, setMsgs] as const;
}
