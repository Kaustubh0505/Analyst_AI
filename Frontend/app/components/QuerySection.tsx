import { useState, useRef, useEffect } from "react";
import { queryData, getExportURL } from "../lib/api";
import { useAnalyst } from "../context/AnalystContext";
import { renderMarkdown } from "../lib/renderMarkdown";

interface QAEntry {
  question: string;
  answer: string;
  intent: string;
  download_available: boolean;
}

const INTENT_COLORS: Record<string, string> = {
  question: "#818cf8",
  manipulation: "#fb923c",
};

const INTENT_ICONS: Record<string, string> = {
  question: "💬",
  manipulation: "⚙️",
};

const SUGGESTIONS = [
  "What is the average value of each numeric column?",
  "Which column has the most null values?",
  "What are the top 5 most frequent values in the category column?",
  "Remove duplicate rows from the dataset",
  "Fill missing values in the age column with the mean",
];

export function QuerySection() {
  const { sessionId, setDownloadAvailable } = useAnalyst();
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<QAEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  async function handleQuery() {
    const q = question.trim();
    if (!q || !sessionId || loading) return;
    setLoading(true);
    setError("");
    try {
      const res = await queryData(q, sessionId);
      setHistory((prev) => [
        ...prev,
        {
          question: q,
          answer: res.answer ?? "(No answer returned)",
          intent: res.intent ?? "question",
          download_available: res.download_available ?? false,
        },
      ]);
      if (res.download_available) setDownloadAvailable(true);
      setQuestion("");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Query failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="query-wrapper">
      <div className="section-header">
        <h2 className="section-title">💬 Ask Your Data</h2>
        {sessionId && <span className="badge badge-green">Session active</span>}
      </div>

      {/* Suggestions */}
      {history.length === 0 && (
        <div className="suggestions">
          <p className="suggestions-label">Try asking:</p>
          <div className="suggestions-list">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                className="suggestion-chip"
                onClick={() => { setQuestion(s); inputRef.current?.focus(); }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat history */}
      <div className="chat-history">
        {history.length === 0 && (
          <div className="chat-empty">
            <span>Start a conversation with your data ↓</span>
          </div>
        )}
        {history.map((entry, i) => (
          <div key={i} className="chat-entry">
            {/* User bubble */}
            <div className="bubble bubble-user">
              <span className="bubble-icon">👤</span>
              <p>{entry.question}</p>
            </div>

            {/* AI bubble */}
            <div className="bubble bubble-ai">
              <span className="bubble-icon">🤖</span>
              <div>
                <div className="bubble-meta">
                  <span
                    className="intent-badge"
                    style={{ borderColor: INTENT_COLORS[entry.intent] ?? "#818cf8", color: INTENT_COLORS[entry.intent] ?? "#818cf8" }}
                  >
                    {INTENT_ICONS[entry.intent] ?? "💬"} {entry.intent}
                  </span>
                </div>
                <p className="bubble-answer">{renderMarkdown(entry.answer)}</p>
                {entry.download_available && sessionId && (
                  <a
                    className="download-link"
                    href={getExportURL(sessionId)}
                    download="exported_data.csv"
                  >
                    ⬇ Download Modified CSV
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="bubble bubble-ai loading-bubble">
            <span className="bubble-icon">🤖</span>
            <div className="typing-dots">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && <div className="status-error">{error}</div>}

      {/* Input */}
      <div className="query-input-row">
        {!sessionId && (
          <p className="upload-hint">⚠️ Upload a file first to start chatting.</p>
        )}
        <div className="query-input-wrap">
          <input
            ref={inputRef}
            id="query-input"
            className="query-input"
            type="text"
            placeholder={sessionId ? "Ask a question or give a data manipulation command…" : "Upload a CSV to get started"}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
            disabled={!sessionId || loading}
          />
          <button
            id="query-submit-btn"
            className="btn-send"
            onClick={handleQuery}
            disabled={!sessionId || loading || !question.trim()}
          >
            {loading ? "…" : "Send ↑"}
          </button>
        </div>
      </div>
    </div>
  );
}
