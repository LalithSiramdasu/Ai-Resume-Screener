import axios from "axios";
import type { UploadResponse, ChatResponse } from "../types";

const api = axios.create({
  baseURL: "/api",
  timeout: 120000, // 2 min timeout for LLM calls
});

function extractErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (error.message) {
      return error.message;
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
}

export async function uploadFiles(
  resume: File,
  jobDescription: File
): Promise<UploadResponse> {
  try {
    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    const response = await api.post<UploadResponse>("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Upload failed. Please try again."));
  }
}

export async function askQuestion(
  sessionId: string,
  question: string
): Promise<ChatResponse> {
  try {
    const response = await api.post<ChatResponse>("/chat", {
      session_id: sessionId,
      question,
    });

    return response.data;
  } catch (error) {
    throw new Error(
      extractErrorMessage(error, "Question could not be processed. Please try again.")
    );
  }
}
