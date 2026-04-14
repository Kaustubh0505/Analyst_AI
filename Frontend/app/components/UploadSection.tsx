import { useState, useRef, useCallback } from "react";
import { uploadCSV, analyzeData } from "../lib/api";
import { useAnalyst } from "../context/AnalystContext";

type Status = "idle" | "uploading" | "analyzing" | "done" | "error";

export function UploadSection({ onDone }: { onDone: () => void }) {
  const { setSessionId, setColumns, setRows, setAnalysisResult } = useAnalyst();
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [progress, setProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.name.endsWith(".csv")) {
      setErrorMsg("Only .csv files are supported.");
      setStatus("error");
      return;
    }
    setFile(f);
    setStatus("idle");
    setErrorMsg("");
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  async function handleUploadAndAnalyze() {
    if (!file) return;
    try {
      setStatus("uploading");
      setProgress(25);
      const uploadRes = await uploadCSV(file);
      setSessionId(uploadRes.session_id);
      setColumns(uploadRes.columns);
      setRows(uploadRes.rows);

      setStatus("analyzing");
      setProgress(60);
      const analysisRes = await analyzeData(uploadRes.session_id);
      setAnalysisResult(analysisRes);

      setProgress(100);
      setStatus("done");
      setTimeout(() => onDone(), 600);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail ?? "Something went wrong. Check that the backend is running.");
      setStatus("error");
      setProgress(0);
    }
  }

  const isLoading = status === "uploading" || status === "analyzing";

  return (
    <div className="upload-wrapper">
      <div className="upload-hero">
        <h2 className="hero-title">Upload your dataset</h2>
        <p className="hero-sub">
          Drop a CSV file and our AI agents will run a full analysis — insights,
          charts, and a professional report — in seconds.
        </p>
      </div>

      {/* Drop zone */}
      <div
        className={`dropzone ${isDragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          id="csv-upload"
          type="file"
          accept=".csv"
          style={{ display: "none" }}
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
        {file ? (
          <div className="file-info">
            <span className="file-icon">📄</span>
            <div>
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
            <button
              className="remove-file"
              onClick={(e) => { e.stopPropagation(); setFile(null); setStatus("idle"); }}
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="dropzone-empty">
            <div className="drop-icon">☁️</div>
            <p className="drop-main">Drag & drop your CSV here</p>
            <p className="drop-sub">or click to browse files</p>
          </div>
        )}
      </div>

      {/* Progress bar */}
      {isLoading && (
        <div className="progress-bar-wrap">
          <div className="progress-bar" style={{ width: `${progress}%` }} />
          <span className="progress-label">
            {status === "uploading" ? "📤 Uploading…" : "🤖 AI agents analyzing…"}
          </span>
        </div>
      )}

      {status === "done" && (
        <div className="status-success">✅ Analysis complete! Switching to Insights…</div>
      )}

      {status === "error" && (
        <div className="status-error">⚠️ {errorMsg}</div>
      )}

      <button
        id="upload-analyze-btn"
        className={`btn-primary ${isLoading ? "loading" : ""}`}
        onClick={handleUploadAndAnalyze}
        disabled={!file || isLoading}
      >
        {status === "uploading"
          ? "Uploading…"
          : status === "analyzing"
          ? "Analyzing with AI…"
          : "Upload & Analyze ✨"}
      </button>

      <div className="pipeline-steps">
        <div className={`step ${progress >= 25 ? "active" : ""}`}>
          <span className="step-icon">📤</span>
          <span>Upload</span>
        </div>
        <div className="step-arrow">→</div>
        <div className={`step ${progress >= 60 ? "active" : ""}`}>
          <span className="step-icon">🧹</span>
          <span>Clean</span>
        </div>
        <div className="step-arrow">→</div>
        <div className={`step ${progress >= 75 ? "active" : ""}`}>
          <span className="step-icon">📊</span>
          <span>EDA</span>
        </div>
        <div className="step-arrow">→</div>
        <div className={`step ${progress >= 90 ? "active" : ""}`}>
          <span className="step-icon">💡</span>
          <span>Insights</span>
        </div>
        <div className="step-arrow">→</div>
        <div className={`step ${progress >= 100 ? "active" : ""}`}>
          <span className="step-icon">📄</span>
          <span>Report</span>
        </div>
      </div>
    </div>
  );
}
