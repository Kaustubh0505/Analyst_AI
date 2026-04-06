import { useState } from "react";
import { fetchReport } from "../lib/api";
import { useAnalyst } from "../context/AnalystContext";

export function ReportSection() {
  const { sessionId, report, setReport } = useAnalyst();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleFetchReport() {
    if (!sessionId) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetchReport(sessionId);
      setReport(res.report);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Failed to fetch report. Make sure /analyze has been run first."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleDownloadReport() {
    if (!report) return;
    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "analyst_report.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="report-wrapper">
      <div className="section-header">
        <h2 className="section-title">📄 Analyst Report</h2>
        {report && (
          <button className="btn-outline" onClick={handleDownloadReport}>
            ⬇ Download
          </button>
        )}
      </div>

      {!sessionId && (
        <div className="status-warn">⚠️ Upload and analyze a CSV first to generate a report.</div>
      )}

      {!report && sessionId && (
        <div className="report-placeholder">
          <div className="report-placeholder-icon">📋</div>
          <h3>Report not loaded yet</h3>
          <p>
            The AI has compiled a professional analyst report from your data. Click below to load it.
          </p>
          <button
            id="fetch-report-btn"
            className={`btn-primary ${loading ? "loading" : ""}`}
            onClick={handleFetchReport}
            disabled={loading || !sessionId}
          >
            {loading ? "Loading report…" : "Load Full Report"}
          </button>
        </div>
      )}

      {error && <div className="status-error">{error}</div>}

      {report && (
        <div className="report-content">
          <div className="report-actions">
            <button
              id="fetch-report-btn"
              className="btn-outline"
              onClick={handleFetchReport}
              disabled={loading}
            >
              {loading ? "Refreshing…" : "🔄 Refresh Report"}
            </button>
          </div>
          <div className="report-sections">
            {report.split(/\n(?=\d+\.\s)/).map((section, i) => (
              <div key={i} className="report-section-card">
                <pre className="report-text">{section.trim()}</pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
