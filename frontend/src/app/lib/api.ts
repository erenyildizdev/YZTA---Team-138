const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000/api";

const ACCESS_TOKEN_KEY = "fikirlab_access_token";

export class ApiError extends Error {
  status: number;
  data?: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
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

  if (response.status === 401) {
    setAccessToken(null);

    sessionStorage.setItem(
      "auth_message",
      "Oturumunuz geçersiz veya süresi dolmuş. Lütfen tekrar giriş yapın.",
    );

    if (window.location.pathname !== "/login") {
      window.location.replace("/login");
    }

    throw new ApiError(
      "Oturumunuz geçersiz veya süresi dolmuş.",
      response.status,
      body,
    );
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

    throw new ApiError(
      message ?? `İstek başarısız oldu (${response.status}).`,
      response.status,
      body,
    );
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

export interface GenericDetailResponse {
  detail: string;
}

export interface RegisterVerificationResponse extends GenericDetailResponse {
  email: string;
  requires_email_verification: true;
}

export interface VerifyEmailPayload {
  email: string;
  code: string;
}

export type VerifyEmailResponse = GenericDetailResponse;

export interface ResendVerificationPayload {
  email: string;
}

export interface PasswordResetRequestPayload {
  email: string;
}

export interface PasswordResetConfirmPayload {
  email: string;
  code: string;
  new_password: string;
  new_password_confirm: string;
}

export interface EmailNotVerifiedErrorPayload extends GenericDetailResponse {
  code: "email_not_verified";
  email: string;
}

export function isEmailNotVerifiedErrorPayload(
  value: unknown,
): value is EmailNotVerifiedErrorPayload {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value) &&
    (value as Record<string, unknown>).code === "email_not_verified" &&
    typeof (value as Record<string, unknown>).email === "string" &&
    typeof (value as Record<string, unknown>).detail === "string"
  );
}

export function register(
  payload: RegisterPayload,
): Promise<RegisterVerificationResponse> {
  return request<RegisterVerificationResponse>("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function verifyEmail(
  payload: VerifyEmailPayload,
): Promise<VerifyEmailResponse> {
  return request<VerifyEmailResponse>("/auth/verify-email/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function resendEmailVerification(
  payload: ResendVerificationPayload,
): Promise<GenericDetailResponse> {
  return request<GenericDetailResponse>("/auth/resend-verification/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function requestPasswordReset(
  payload: PasswordResetRequestPayload,
): Promise<GenericDetailResponse> {
  return request<GenericDetailResponse>("/auth/password-reset/request/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function confirmPasswordReset(
  payload: PasswordResetConfirmPayload,
): Promise<GenericDetailResponse> {
  return request<GenericDetailResponse>("/auth/password-reset/confirm/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export type AccountProfile = AuthUser;

export interface UpdateAccountProfilePayload {
  first_name?: string;
  last_name?: string;
}

export function getCurrentUserProfile(
  signal?: AbortSignal,
): Promise<AccountProfile> {
  return request<AccountProfile>("/auth/me/", { signal });
}

export function updateCurrentUserProfile(
  payload: UpdateAccountProfilePayload,
): Promise<AccountProfile> {
  return request<AccountProfile>("/auth/me/", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export const getProfile = getCurrentUserProfile;
export type UpdateProfilePayload = UpdateAccountProfilePayload;
export const updateProfile = updateCurrentUserProfile;

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface ChangePasswordResponse {
  detail: string;
  requires_reauthentication: boolean;
}

export function changeCurrentUserPassword(
  payload: ChangePasswordPayload,
): Promise<ChangePasswordResponse> {
  return request<ChangePasswordResponse>("/auth/change-password/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export const changePassword = changeCurrentUserPassword;

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

export interface RagSource {
  title: string;
  source_type: string;
  source_url?: string | null;
  chunk_id: number;
  chunk_index: number;
  distance: number;
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

  sources: RagSource[];
}

export function createIdea(payload: IdeaPayload): Promise<IdeaResponse> {
  return request<IdeaResponse>("/ideas/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateIdea(
  ideaId: number,
  payload: Partial<IdeaPayload>,
): Promise<IdeaResponse> {
  return request<IdeaResponse>(`/ideas/${ideaId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export interface IdeaComparisonRiskyAssumptions {
  total: number;
  validated: number;
  refuted: number;
  untested: number;
  high_risk: number;
}

export interface IdeaComparisonMoscow {
  must_have: number;
  should_have: number;
  could_have: number;
  wont_have: number;
}

export interface IdeaComparisonResult {
  id: number;
  title: string;
  sector: string;
  target_audience: string;
  analysis_status: "draft" | "in_progress" | "completed";
  created_at: string;
  risky_assumptions: IdeaComparisonRiskyAssumptions;
  moscow: IdeaComparisonMoscow;
  mom_test_question_count: number;
  interview_note_count: number;
  competitor_analysis_summary: string;
  general_evaluation_summary: string;
}

export interface CompareIdeasResponse {
  ideas: IdeaComparisonResult[];
}

export function compareIdeas(ideaIds: number[]): Promise<CompareIdeasResponse> {
  return request<CompareIdeasResponse>(`/ideas/compare/?ids=${ideaIds.join(",")}`);
}

const VALIDATION_WORKFLOW_STEP_NAMES = [
  "risky_assumptions",
  "mom_test_questions",
  "moscow_scope",
  "validation_roadmap",
  "general_evaluation",
] as const;

export type ValidationWorkflowStepName =
  (typeof VALIDATION_WORKFLOW_STEP_NAMES)[number];

export interface ValidationWorkflowStepResult {
  name: ValidationWorkflowStepName;
  status: "completed";
  result: unknown;
}

export interface ValidationWorkflowSuccessResponse {
  idea_id: number;
  status: "completed";
  completed_steps: ValidationWorkflowStepName[];
  steps: ValidationWorkflowStepResult[];
}

export interface ValidationWorkflowFailureResponse {
  idea_id: number;
  status: "failed";
  completed_steps: ValidationWorkflowStepName[];
  failed_step: ValidationWorkflowStepName;
  error_code: string;
  detail: string;
  steps: ValidationWorkflowStepResult[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isValidationWorkflowStepName(
  value: unknown,
): value is ValidationWorkflowStepName {
  return (
    typeof value === "string" &&
    VALIDATION_WORKFLOW_STEP_NAMES.some((stepName) => stepName === value)
  );
}

function isValidationWorkflowStepResult(
  value: unknown,
): value is ValidationWorkflowStepResult {
  return (
    isRecord(value) &&
    isValidationWorkflowStepName(value.name) &&
    value.status === "completed" &&
    "result" in value
  );
}

export function isValidationWorkflowFailureResponse(
  value: unknown,
): value is ValidationWorkflowFailureResponse {
  if (
    !isRecord(value) ||
    typeof value.idea_id !== "number" ||
    !Number.isInteger(value.idea_id) ||
    value.idea_id <= 0 ||
    value.status !== "failed" ||
    !Array.isArray(value.completed_steps) ||
    !value.completed_steps.every(isValidationWorkflowStepName) ||
    !isValidationWorkflowStepName(value.failed_step) ||
    typeof value.error_code !== "string" ||
    typeof value.detail !== "string" ||
    !Array.isArray(value.steps) ||
    !value.steps.every(isValidationWorkflowStepResult)
  ) {
    return false;
  }

  const completedSteps = value.completed_steps as ValidationWorkflowStepName[];
  const steps = value.steps as ValidationWorkflowStepResult[];

  return (
    completedSteps.length < VALIDATION_WORKFLOW_STEP_NAMES.length &&
    completedSteps.every(
      (stepName, index) => VALIDATION_WORKFLOW_STEP_NAMES[index] === stepName,
    ) &&
    value.failed_step === VALIDATION_WORKFLOW_STEP_NAMES[completedSteps.length] &&
    steps.length === completedSteps.length &&
    steps.every((stepResult, index) => stepResult.name === completedSteps[index])
  );
}

export function runValidationWorkflow(
  ideaId: number,
): Promise<ValidationWorkflowSuccessResponse> {
  return request<ValidationWorkflowSuccessResponse>(
    `/analyses/ideas/${ideaId}/workflow/`,
    { method: "POST" },
  );
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

export interface PitchSlide {
  title: string;
  bullets: string[];
}

export interface InvestorPitchData {
  elevator_pitch: string;
  slides: PitchSlide[];
  closing_ask: string;
}

export interface InvestorPitchResponse {
  id: number;
  idea: number;
  pitch_data: InvestorPitchData;
  created_at: string;
}

export function getInvestorPitch(ideaId: number): Promise<InvestorPitchResponse> {
  return request<InvestorPitchResponse>(`/ideas/${ideaId}/pitch/`);
}

export function generateInvestorPitch(ideaId: number): Promise<InvestorPitchResponse> {
  return request<InvestorPitchResponse>(`/ideas/${ideaId}/generate-pitch/`, {
    method: "POST",
  });
}

export interface InterviewNotePayload {
  interviewee_name?: string;
  interviewee_profile?: string;
  notes: string;
  interviewed_at?: string | null;
}

export interface InterviewNoteUpdatePayload {
  interviewee_name?: string;
  interviewee_profile?: string;
  notes?: string;
  interviewed_at?: string | null;
}

export interface InterviewNoteResponse {
  id: number;
  idea_id: number;
  interviewee_name: string;
  interviewee_profile: string;
  notes: string;
  interviewed_at: string | null;
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

export function updateInterviewNote(
  ideaId: number,
  noteId: number,
  payload: InterviewNoteUpdatePayload,
): Promise<InterviewNoteResponse> {
  return request<InterviewNoteResponse>(
    `/analyses/ideas/${ideaId}/interview-notes/${noteId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
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
