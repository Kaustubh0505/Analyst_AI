import type { Route } from "./+types/home";
import { useState, useCallback } from "react";
import { UploadSection } from "../components/UploadSection";
import { InsightsSection } from "../components/InsightsSection";
import { ChartsSection } from "../components/ChartsSection";
import { QuerySection } from "../components/QuerySection";
import { ReportSection } from "../components/ReportSection";
import { useAnalyst } from "../context/AnalystContext";
import { getExportURL } from "../lib/api";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Analyst AI — Data Intelligence Platform" },
    { name: "description", content: "AI-powered CSV analysis with LangGraph multi-agent pipeline" },
  ];
}

type Tab = "upload" | "insights" | "charts" | "query" | "report";

const TABS: { id: Tab; icon: string; label: string }[] = [
  { id: "upload",   icon: "📁", label: "Upload"   },
  { id: "insights", icon: "💡", label: "Insights" },
  { id: "charts",   icon: "📊", label: "Charts"   },
  { id: "query",    icon: "💬", label: "Chat"     },
  { id: "report",   icon: "📄", label: "Report"   },
];

const SAMPLE_DATASETS = [
  { name: "Walmart Sales", file: "Walmart.csv", icon: "🛒", description: "Retail sales dataset" },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("upload");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [samplesOpen, setSamplesOpen] = useState(false);
  const [preloadFile, setPreloadFile] = useState<File | null>(null);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);
  const { sessionId, insights, charts, downloadAvailable } = useAnalyst();

  const loadSample = useCallback(async (filename: string) => {
    setLoadingSample(filename);
    try {
      const res = await fetch(`/${filename}`);
      const blob = await res.blob();
      const file = new File([blob], filename, { type: "text/csv" });
      setPreloadFile(file);
      setActiveTab("upload");
      setSidebarOpen(false);
    } catch {
      alert("Could not load sample dataset. Please try again.");
    } finally {
      setLoadingSample(null);
    }
  }, []);

  function handleTabChange(tab: Tab) {
    setActiveTab(tab);
    setSidebarOpen(false); // close sidebar on mobile after nav
  }

  return (
    <div className="app-shell">
      {/* Sidebar overlay (mobile) */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? "" : "hidden"}`}
        onClick={() => setSidebarOpen(false)}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar-brand">
          <span className="brand-logo">🧠</span>
          <span className="brand-name">Analyst AI</span>
        </div>

        <nav className="sidebar-nav">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              className={`nav-item ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => handleTabChange(tab.id)}
            >
              <span className="nav-icon">{tab.icon}</span>
              <span className="nav-label">{tab.label}</span>
              {tab.id === "insights" && insights.length > 0 && (
                <span className="nav-count">{insights.length}</span>
              )}
              {tab.id === "charts" && charts.length > 0 && (
                <span className="nav-count">{charts.length}</span>
              )}
            </button>
          ))}
        </nav>

        {/* Sample Datasets Section */}
        <div className="sidebar-samples">
          <button
            id="sidebar-samples-toggle"
            className="samples-toggle"
            onClick={() => setSamplesOpen((o) => !o)}
            aria-expanded={samplesOpen}
          >
            <span className="nav-icon">🗂️</span>
            <span className="nav-label">Sample Datasets</span>
            <span className={`samples-chevron ${samplesOpen ? "open" : ""}`}>›</span>
          </button>

          {samplesOpen && (
            <div className="samples-list">
              {SAMPLE_DATASETS.map((ds) => (
                <button
                  key={ds.file}
                  id={`sample-${ds.file}`}
                  className="sample-item"
                  onClick={() => loadSample(ds.file)}
                  disabled={loadingSample === ds.file}
                  title={ds.description}
                >
                  <span className="sample-icon">{ds.icon}</span>
                  <div className="sample-meta">
                    <span className="sample-name">{ds.name}</span>
                    <span className="sample-desc">{ds.description}</span>
                  </div>
                  {loadingSample === ds.file ? (
                    <span className="sample-loading">⏳</span>
                  ) : (
                    <span className="sample-arrow">↑</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          {downloadAvailable && sessionId && (
            <a
              href={getExportURL(sessionId)}
              className="sidebar-download-btn"
              download="cleaned_data.csv"
              title="Download the processed dataset"
            >
              <span className="nav-icon">📥</span>
              <span className="nav-label">Download Cleaned CSV</span>
            </a>
          )}
          <div className={`session-indicator ${sessionId ? "connected" : "disconnected"}`}>
            <span className="session-dot" />
            {sessionId ? "Session active" : "No session"}
          </div>
          <p className="sidebar-tagline">Powered by LangGraph + Gemini</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        {/* Top bar */}
        <header className="topbar">
          {/* Hamburger — visible only on mobile via CSS */}
          <button
            className="hamburger-btn"
            aria-label="Open menu"
            onClick={() => setSidebarOpen((o) => !o)}
          >
            ☰
          </button>

          <div className="topbar-title">
            {TABS.find((t) => t.id === activeTab)?.icon}{" "}
            {TABS.find((t) => t.id === activeTab)?.label}
          </div>
          {sessionId && (
            <div className="topbar-session">
              Session: <code>{sessionId}</code>
            </div>
          )}
        </header>

        {/* Panels */}
        <div className="panel">
          {activeTab === "upload" && (
            <UploadSection
              onDone={() => setActiveTab("insights")}
              preloadFile={preloadFile}
            />
          )}
          {activeTab === "insights" && <InsightsSection />}
          {activeTab === "charts"   && <ChartsSection />}
          {activeTab === "query"    && <QuerySection />}
          {activeTab === "report"   && <ReportSection />}
        </div>
      </main>

      {/* Bottom nav — visible only on mobile via CSS */}
      <nav className="bottom-nav" aria-label="Mobile navigation">
        <div className="bottom-nav-inner">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`bottom-nav-item ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => handleTabChange(tab.id)}
              aria-label={tab.label}
            >
              <span className="bn-icon">{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.id === "insights" && insights.length > 0 && (
                <span className="bn-count">{insights.length}</span>
              )}
              {tab.id === "charts" && charts.length > 0 && (
                <span className="bn-count">{charts.length}</span>
              )}
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}
