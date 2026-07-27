const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000/api";

const ACCESS_TOKEN_KEY = "fikirlab_access_token";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string | null): void {
  if (token) localStorage.setItem(ACCESS_TOKEN_KEY, token);
  else localStorage.removeItem(ACCESS_TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 204) return undefined as T;

  const text = await response.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    let message: string | null = null;

    if (body && typeof body === "object") {
      const anyBody = body as Record<string, unknown>;
      if ("detail" in anyBody || "message" in anyBody) {
        message = String(anyBody.detail ?? anyBody.message);
      } else {
        const fieldErrors = Object.entries(anyBody)
          .map(([field, value]) => (Array.isArray(value) ? `${field}: ${value.join(" ")}` : null))
          .filter((part): part is string => Boolean(part));
        if (fieldErrors.length) message = fieldErrors.join(" ");
      }
    } else if (typeof body === "string" && body) {
      message = body;
    }

    throw new ApiError(message ?? `İstek başarısız oldu (${response.status}).`, response.status);
  }

  return body as T;
}

export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface RegisterResponse {
  message: string;
  user: AuthUser;
}

export function register(payload: RegisterPayload): Promise<RegisterResponse> {
  return request<RegisterResponse>("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface ValidationRoadmapPhase {
  week?: number;
  phase?: number;
  title?: string;
  [section: string]: unknown;
}

export interface ValidationRoadmapData {
  roadmap_type?: string;
  idea_title?: string;
  phases: ValidationRoadmapPhase[];
}

export interface ValidationRoadmapResponse {
  id: number;
  idea: number;
  roadmap_data: ValidationRoadmapData;
  created_at: string;
}

export function getValidationRoadmap(ideaId: number): Promise<ValidationRoadmapResponse> {
  return request<ValidationRoadmapResponse>(`/ideas/${ideaId}/roadmap/`);
}

export function generateValidationRoadmap(ideaId: number): Promise<ValidationRoadmapResponse> {
  return request<ValidationRoadmapResponse>(`/ideas/${ideaId}/generate-roadmap/`, {
    method: "POST",
  });
}

export interface IdeaPayload {
  title: string;
  description: string;
  target_audience: string;
  problem: string;
  solution: string;
  sector: string;
}

export interface IdeaResponse extends IdeaPayload {
  id: number;
  created_at: string;
  analysis_status: "draft" | "in_progress" | "completed";
  completed_analysis_count: number;
  total_analysis_count: number;
}

export function createIdea(payload: IdeaPayload): Promise<IdeaResponse> {
  return request<IdeaResponse>("/ideas/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getIdea(ideaId: number): Promise<IdeaResponse> {
  return request<IdeaResponse>(`/ideas/${ideaId}/`);
}

export function deleteIdea(ideaId: number): Promise<void> {
  return request<void>(`/ideas/${ideaId}/`, {
    method: "DELETE",
  });
}

interface PaginatedResponse<T> {
  results: T[];
}

export async function getIdeas(): Promise<IdeaResponse[]> {
  const response = await request<IdeaResponse[] | PaginatedResponse<IdeaResponse>>("/ideas/");
  return Array.isArray(response) ? response : response.results;
}

export interface RiskyAssumptionItem {
  text: string;
  level: "high" | "medium" | "low";
  status?: "validated" | "refuted" | "untested";
  evidence_quote?: string;
}

export interface RiskyAssumptionsData {
  assumptions: RiskyAssumptionItem[];
}

export interface RiskyAssumptionsResponse {
  id: number;
  idea: number;
  assumptions_data: RiskyAssumptionsData;
  created_at: string;
}

export function getRiskyAssumptions(ideaId: number): Promise<RiskyAssumptionsResponse> {
  return request<RiskyAssumptionsResponse>(`/ideas/${ideaId}/risky-assumptions/`);
}

export function generateRiskyAssumptions(ideaId: number): Promise<RiskyAssumptionsResponse> {
  return request<RiskyAssumptionsResponse>(`/ideas/${ideaId}/generate-risky-assumptions/`, {
    method: "POST",
  });
}

export interface MoscowFeatureItem {
  title: string;
  reason: string;
}

export interface MoscowScopeData {
  summary: string;
  must_have: MoscowFeatureItem[];
  should_have: MoscowFeatureItem[];
  could_have: MoscowFeatureItem[];
  wont_have: MoscowFeatureItem[];
}

export interface MoscowScopeResponse extends MoscowScopeData {
  id: number;
  idea_id: number;
  prompt_version: string;
  provider: string;
  model_name: string;
  created_at: string;
  updated_at: string;
}

export function getMoscowScope(ideaId: number): Promise<MoscowScopeResponse> {
  return request<MoscowScopeResponse>(`/analyses/ideas/${ideaId}/moscow-scope/`);
}

export function generateMoscowScope(ideaId: number): Promise<MoscowScopeResponse> {
  return request<MoscowScopeResponse>(`/analyses/ideas/${ideaId}/moscow-scope/`, {
    method: "POST",
  });
}

export interface MomTestQuestionItem {
  category: string;
  question: string;
}

export interface MomTestQuestionsResponse {
  idea_id: number;
  framework: string;
  question_count: number;
  questions: MomTestQuestionItem[];
}

export function generateMomTestQuestions(
  ideaId: number,
  questionCount = 10,
): Promise<MomTestQuestionsResponse> {
  return request<MomTestQuestionsResponse>(`/analyses/ideas/${ideaId}/mom-test-questions/`, {
    method: "POST",
    body: JSON.stringify({ question_count: questionCount }),
  });
}

export function getMomTestQuestions(ideaId: number): Promise<MomTestQuestionsResponse> {
  return request<MomTestQuestionsResponse>(`/analyses/ideas/${ideaId}/mom-test-questions/`);
}

export interface GeneralEvaluationData {
  strengths: string[];
  uncertainties: string[];
  next_action: string;
}

export interface GeneralEvaluationResponse {
  id: number;
  idea: number;
  evaluation_data: GeneralEvaluationData;
  created_at: string;
}

export function getGeneralEvaluation(ideaId: number): Promise<GeneralEvaluationResponse> {
  return request<GeneralEvaluationResponse>(`/ideas/${ideaId}/evaluation/`);
}

export function generateGeneralEvaluation(ideaId: number): Promise<GeneralEvaluationResponse> {
  return request<GeneralEvaluationResponse>(`/ideas/${ideaId}/generate-evaluation/`, {
    method: "POST",
  });
}

export interface CompetitorItem {
  name: string;
  description: string;
  strengths: string[];
  weaknesses: string[];
}

export interface CompetitorAnalysisData {
  competitors: CompetitorItem[];
  market_gap: string;
  differentiation: string;
}

export interface CompetitorAnalysisResponse {
  id: number;
  idea: number;
  analysis_data: CompetitorAnalysisData;
  created_at: string;
}

export function getCompetitorAnalysis(ideaId: number): Promise<CompetitorAnalysisResponse> {
  return request<CompetitorAnalysisResponse>(`/ideas/${ideaId}/competitor-analysis/`);
}

export function generateCompetitorAnalysis(ideaId: number): Promise<CompetitorAnalysisResponse> {
  return request<CompetitorAnalysisResponse>(`/ideas/${ideaId}/generate-competitor-analysis/`, {
    method: "POST",
  });
}

export interface InterviewNotePayload {
  interviewee_name?: string;
  interviewee_profile?: string;
  notes: string;
  interviewed_at?: string | null;
}

export interface InterviewNoteResponse extends InterviewNotePayload {
  id: number;
  idea_id: number;
  created_at: string;
  updated_at: string;
}

export function getInterviewNotes(ideaId: number): Promise<InterviewNoteResponse[]> {
  return request<InterviewNoteResponse[]>(`/analyses/ideas/${ideaId}/interview-notes/`);
}

export function createInterviewNote(
  ideaId: number,
  payload: InterviewNotePayload,
): Promise<InterviewNoteResponse> {
  return request<InterviewNoteResponse>(`/analyses/ideas/${ideaId}/interview-notes/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteInterviewNote(ideaId: number, noteId: number): Promise<void> {
  return request<void>(`/analyses/ideas/${ideaId}/interview-notes/${noteId}/`, {
    method: "DELETE",
  });
}

export interface InterviewEvidenceAnalysisData {
  supporting_evidence: string[];
  contradicting_evidence: string[];
  repeated_needs: string[];
  new_risky_assumptions: string[];
  next_validation_steps: string[];
}

export interface InterviewEvidenceAnalysisResponse {
  id: number;
  idea: number;
  result: InterviewEvidenceAnalysisData;
  created_at: string;
}

export function getInterviewEvidenceAnalysis(ideaId: number): Promise<InterviewEvidenceAnalysisResponse> {
  return request<InterviewEvidenceAnalysisResponse>(`/analyses/ideas/${ideaId}/interview-evidence-analysis/`);
}

export interface MentorChatHistoryTurn {
  role: "user" | "assistant";
  content: string;
}

export interface MentorChatAction {
  tool: string;
  status: "success" | "error";
  result: Record<string, unknown>;
}

export interface MentorChatResponse {
  reply: string;
  actions: MentorChatAction[];
}

export function sendMentorMessage(
  ideaId: number,
  message: string,
  history: MentorChatHistoryTurn[] = [],
): Promise<MentorChatResponse> {
  return request<MentorChatResponse>(`/ideas/${ideaId}/mentor-chat/`, {
    method: "POST",
    body: JSON.stringify({ message, history }),
  });
}
