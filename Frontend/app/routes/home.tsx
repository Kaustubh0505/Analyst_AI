import type { Route } from "./+types/home";
import { useState } from "react";
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

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("upload");
  const { sessionId, insights, charts } = useAnalyst();

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
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
              onClick={() => setActiveTab(tab.id)}
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

        <div className="sidebar-footer">
          {sessionId && (
            <a
              href={getExportURL(sessionId)}
              className="sidebar-download-btn"
              download="cleaned_data.csv"
              title="Download the processed dataset"
            >
              <span className="nav-icon">📥</span>
              <span className="nav-label">Download CSV</span>
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
            <UploadSection onDone={() => setActiveTab("insights")} />
          )}
          {activeTab === "insights" && <InsightsSection />}
          {activeTab === "charts"   && <ChartsSection />}
          {activeTab === "query"    && <QuerySection />}
          {activeTab === "report"   && <ReportSection />}
        </div>
      </main>
    </div>
  );
}
