import type { MatchResult } from "../types";
import "./MatchAnalysis.css";

interface MatchAnalysisProps {
  result: MatchResult;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "var(--success)";
  if (score >= 60) return "var(--info)";
  if (score >= 40) return "var(--warning)";
  return "var(--danger)";
}

function getScoreLabel(score: number): string {
  if (score >= 80) return "Excellent Match";
  if (score >= 60) return "Good Match";
  if (score >= 40) return "Moderate Match";
  return "Needs Improvement";
}

export default function MatchAnalysis({ result }: MatchAnalysisProps) {
  const color = getScoreColor(result.score);
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (result.score / 100) * circumference;

  return (
    <div className="match-container">
      <div className="match-header">
        <h2>📊 Match Analysis</h2>
      </div>

      <div className="match-content">
        <div className="score-section">
          <div className="score-ring">
            <svg viewBox="0 0 120 120" className="score-svg">
              <circle cx="60" cy="60" r="54" fill="none" stroke="var(--border)" strokeWidth="8" />
              <circle
                cx="60" cy="60" r="54"
                fill="none"
                stroke={color}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                transform="rotate(-90 60 60)"
                style={{ transition: "stroke-dashoffset 1s ease" }}
              />
            </svg>
            <div className="score-text">
              <span className="score-number" style={{ color }}>{result.score}%</span>
              <span className="score-label">{getScoreLabel(result.score)}</span>
            </div>
          </div>
        </div>

        <div className="details-section">
          {result.strengths.length > 0 && (
            <div className="detail-group">
              <h3>✅ Strengths</h3>
              <ul>
                {result.strengths.map((s, i) => (
                  <li key={i} className="strength-item">{s}</li>
                ))}
              </ul>
            </div>
          )}

          {result.gaps.length > 0 && (
            <div className="detail-group">
              <h3>❌ Gaps</h3>
              <ul>
                {result.gaps.map((g, i) => (
                  <li key={i} className="gap-item">{g}</li>
                ))}
              </ul>
            </div>
          )}

          {result.insights.length > 0 && (
            <div className="detail-group">
              <h3>💡 Key Insights</h3>
              <ul>
                {result.insights.map((ins, i) => (
                  <li key={i} className="insight-item">{ins}</li>
                ))}
              </ul>
            </div>
          )}

          {result.assessment && (
            <div className="assessment-box">
              <h3>📝 Overall Assessment</h3>
              <p>{result.assessment}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
