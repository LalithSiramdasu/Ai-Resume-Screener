import { useState } from "react";
import FileUpload from "./components/FileUpload";
import MatchAnalysis from "./components/MatchAnalysis";
import ChatInterface from "./components/ChatInterface";
import ResumeHighlights from "./components/ResumeHighlights";
import { uploadFiles } from "./services/api";
import type { MatchResult, ResumeData } from "./types";
import "./App.css";

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (resume: File, jobDescription: File) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await uploadFiles(resume, jobDescription);
      setSessionId(response.session_id);
      setMatchResult(response.match_result);
      setResumeData(response.resume_data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Upload failed. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setMatchResult(null);
    setResumeData(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🎯</span>
            <h1>Resume Screening Tool</h1>
          </div>
          <p className="tagline">AI-Powered Resume Analysis with RAG</p>
          {sessionId && (
            <button className="reset-btn" onClick={handleReset}>
              📄 New Analysis
            </button>
          )}
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {!sessionId ? (
          <div className="upload-section">
            <FileUpload onUpload={handleUpload} isLoading={isLoading} />
          </div>
        ) : (
          <div className="results-section">
            {matchResult && <MatchAnalysis result={matchResult} />}

            <div className="two-columns">
              {resumeData && <ResumeHighlights data={resumeData} />}
              <ChatInterface sessionId={sessionId} />
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Built with FastAPI + React + Gemini + ChromaDB | RAG-powered Resume
          Screening
        </p>
      </footer>
    </div>
  );
}

export default App;
