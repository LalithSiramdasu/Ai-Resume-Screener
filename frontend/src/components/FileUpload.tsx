import { useState } from "react";
import "./FileUpload.css";

interface FileUploadProps {
  onUpload: (resume: File, jobDescription: File) => void;
  isLoading: boolean;
}

export default function FileUpload({ onUpload, isLoading }: FileUploadProps) {
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<File | null>(null);
  const [resumeDrag, setResumeDrag] = useState(false);
  const [jdDrag, setJdDrag] = useState(false);

  const isSupportedFile = (file: File) => {
    const normalizedName = file.name.toLowerCase();
    return normalizedName.endsWith(".pdf") || normalizedName.endsWith(".txt");
  };

  const handleDrop = (
    e: React.DragEvent,
    setter: (f: File) => void,
    setDrag: (d: boolean) => void
  ) => {
    e.preventDefault();
    setDrag(false);
    const file = e.dataTransfer.files[0];
    if (file && isSupportedFile(file)) {
      setter(file);
    }
  };

  const handleSubmit = () => {
    if (resume && jobDescription) {
      onUpload(resume, jobDescription);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <div className="upload-icon">📄</div>
        <h2>Upload Documents</h2>
        <p>Upload a resume and job description to get started</p>
      </div>

      <div className="upload-zones">
        <div
          className={`drop-zone ${resumeDrag ? "drag-over" : ""} ${resume ? "has-file" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setResumeDrag(true); }}
          onDragLeave={() => setResumeDrag(false)}
          onDrop={(e) => handleDrop(e, setResume, setResumeDrag)}
          onClick={() => document.getElementById("resume-input")?.click()}
        >
          <input
            id="resume-input"
            type="file"
            accept=".pdf,.txt"
            hidden
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file && isSupportedFile(file)) {
                setResume(file);
              }
            }}
          />
          <div className="drop-icon">{resume ? "✅" : "📋"}</div>
          <span className="drop-label">
            {resume ? resume.name : "Drop Resume Here"}
          </span>
          <span className="drop-hint">PDF or TXT</span>
        </div>

        <div
          className={`drop-zone ${jdDrag ? "drag-over" : ""} ${jobDescription ? "has-file" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setJdDrag(true); }}
          onDragLeave={() => setJdDrag(false)}
          onDrop={(e) => handleDrop(e, setJobDescription, setJdDrag)}
          onClick={() => document.getElementById("jd-input")?.click()}
        >
          <input
            id="jd-input"
            type="file"
            accept=".pdf,.txt"
            hidden
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file && isSupportedFile(file)) {
                setJobDescription(file);
              }
            }}
          />
          <div className="drop-icon">{jobDescription ? "✅" : "💼"}</div>
          <span className="drop-label">
            {jobDescription ? jobDescription.name : "Drop Job Description Here"}
          </span>
          <span className="drop-hint">PDF or TXT</span>
        </div>
      </div>

      <button
        className="upload-btn"
        disabled={!resume || !jobDescription || isLoading}
        onClick={handleSubmit}
      >
        {isLoading ? (
          <>
            <span className="spinner"></span>
            Analyzing...
          </>
        ) : (
          <>🚀 Analyze Match</>
        )}
      </button>
    </div>
  );
}
