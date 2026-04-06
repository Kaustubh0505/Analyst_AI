import { useAnalyst } from "../context/AnalystContext";

export function InsightsSection() {
  const { insights, edaSummary, columns, rows } = useAnalyst();

  if (!insights.length && !edaSummary) {
    return (
      <div className="empty-state">
        <div className="empty-icon">💡</div>
        <h3>No insights yet</h3>
        <p>Upload and analyze a CSV file first to see AI-generated insights.</p>
      </div>
    );
  }

  return (
    <div className="insights-wrapper">
      {/* Dataset Overview Stats */}
      {(edaSummary || columns.length > 0) && (
        <div className="stat-grid">
          <div className="stat-card">
            <span className="stat-icon">📋</span>
            <div className="stat-value">{edaSummary?.shape?.rows ?? rows ?? "—"}</div>
            <div className="stat-label">Total Rows</div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📐</span>
            <div className="stat-value">{edaSummary?.shape?.cols ?? columns.length ?? "—"}</div>
            <div className="stat-label">Columns</div>
          </div>
          <div className="stat-card wide">
            <span className="stat-icon">🗂️</span>
            <div className="stat-label" style={{ marginBottom: 6 }}>Column Names</div>
            <div className="column-tags">
              {columns.map((col) => (
                <span key={col} className="tag">{col}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Insights */}
      <div className="section-header">
        <h2 className="section-title">🔍 Key Insights</h2>
        <span className="badge">{insights.length} findings</span>
      </div>

      <div className="insights-list">
        {insights.map((insight, i) => (
          <div key={i} className="insight-card" style={{ animationDelay: `${i * 60}ms` }}>
            <div className="insight-number">{String(i + 1).padStart(2, "0")}</div>
            <p className="insight-text">{insight}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
