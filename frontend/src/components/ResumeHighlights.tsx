import type { ResumeData } from "../types";
import "./ResumeHighlights.css";

interface ResumeHighlightsProps {
  data: ResumeData;
}

export default function ResumeHighlights({ data }: ResumeHighlightsProps) {
  return (
    <div className="highlights-container">
      <div className="highlights-header">
        <h2>📋 Resume Highlights</h2>
      </div>

      {data.summary && (
        <div className="highlight-section">
          <h3>📝 Summary</h3>
          <p className="summary-text">{data.summary}</p>
        </div>
      )}

      {data.skills.length > 0 && (
        <div className="highlight-section">
          <h3>🛠 Skills</h3>
          <div className="skills-grid">
            {data.skills.map((skill, i) => (
              <span key={i} className="skill-badge">{skill}</span>
            ))}
          </div>
        </div>
      )}

      {data.experience.length > 0 && (
        <div className="highlight-section">
          <h3>💼 Experience</h3>
          <ul className="detail-list">
            {data.experience.map((exp, i) => (
              <li key={i}>{exp}</li>
            ))}
          </ul>
        </div>
      )}

      {data.education.length > 0 && (
        <div className="highlight-section">
          <h3>🎓 Education</h3>
          <ul className="detail-list">
            {data.education.map((edu, i) => (
              <li key={i}>{edu}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
