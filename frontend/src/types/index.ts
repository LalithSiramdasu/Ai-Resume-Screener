export interface MatchResult {
  score: number;
  strengths: string[];
  gaps: string[];
  insights: string[];
  assessment: string;
}

export interface ResumeData {
  raw_text: string;
  skills: string[];
  experience: string[];
  education: string[];
  summary: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface UploadResponse {
  session_id: string;
  match_result: MatchResult;
  resume_data: ResumeData;
}

export interface ChatResponse {
  answer: string;
  chat_history: ChatMessage[];
}
