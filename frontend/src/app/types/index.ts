export type RiskLevel = "high" | "medium" | "low";
export type IdeaStatus = "draft" | "complete";

export interface IdeaCard {
  id: string;
  title: string;
  description: string;
  sector: string;
  targetAudience: string;
  status: IdeaStatus;
  date: string;
}

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
