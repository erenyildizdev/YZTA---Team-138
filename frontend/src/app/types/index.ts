export type RiskLevel = "high" | "medium" | "low";
export type IdeaStatus = "draft" | "in_progress" | "completed";

export interface ChatMessageAction {
  tool: string;
  status: "success" | "error";
  result?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  actions?: ChatMessageAction[];
}
