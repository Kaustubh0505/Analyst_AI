import { useState } from "react";
import { useAnalyst } from "../context/AnalystContext";
import type { ChartSpec } from "../context/AnalystContext";
import { analyzeData } from "../lib/api";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = ["#818cf8", "#38bdf8", "#fb923c", "#34d399", "#f87171", "#c084fc"];

const CHART_TYPE_LABELS: Record<string, string> = {
  bar: "Bar Chart",
  line: "Line Chart",
  scatter: "Scatter Plot",
  histogram: "Histogram",
  pie: "Pie Chart",
  heatmap: "Heatmap",
};

function ChartCard({ chart, index, data }: { chart: ChartSpec; index: number; data: any[] }) {
  const color = COLORS[index % COLORS.length];

  return (
    <div className="chart-card" style={{ animationDelay: `${index * 80}ms` }}>
      <div className="chart-card-header">
        <div>
          <h3 className="chart-title">{chart.title}</h3>
          <div className="chart-meta">
            <span className="tag">{CHART_TYPE_LABELS[chart.type] ?? chart.type}</span>
            {chart.x && <span className="tag tag-dim">X: {chart.x}</span>}
            {chart.y && <span className="tag tag-dim">Y: {chart.y}</span>}
          </div>
        </div>
      </div>

      <div className="chart-canvas">
        <ResponsiveContainer width="100%" height={220}>
          {chart.type === "bar" || chart.type === "histogram" ? (
            <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey={chart.x || "x"} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0" }}
              />
              <Bar dataKey={chart.y || "y"} fill={color} radius={[4, 4, 0, 0]} />
            </BarChart>
          ) : chart.type === "line" ? (
            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey={chart.x || "x"} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0" }}
              />
              <Line
                type="monotone"
                dataKey={chart.y || "y"}
                stroke={color}
                strokeWidth={2}
                dot={{ fill: color, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          ) : chart.type === "pie" ? (
            <PieChart>
              <Pie
                data={data}
                dataKey={chart.y || "y"}
                nameKey={chart.x || "x"}
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {data.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0" }}
              />
            </PieChart>
          ) : chart.type === "scatter" ? (
            <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey={chart.x || "x"} name={chart.x} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis dataKey={chart.y || "y"} name={chart.y} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0" }}
                cursor={{ strokeDasharray: "3 3" }}
              />
              <Scatter data={data} fill={color} />
            </ScatterChart>
          ) : (
            // Fallback: bar
            <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey={chart.x || "x"} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0" }}
              />
              <Bar dataKey={chart.y || "y"} fill={color} radius={[4, 4, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      <p className="chart-note">
        ℹ️ Visualizing top 25 rows from your cleaned dataset.
      </p>
    </div>
  );
}

export function ChartsSection() {
  const { charts, chartData, sessionId, setAnalysisResult } = useAnalyst();
  const [isRefreshing, setIsRefreshing] = useState(false);

  async function handleRefresh() {
    if (!sessionId) return;
    try {
      setIsRefreshing(true);
      const res = await analyzeData(sessionId);
      setAnalysisResult(res);
    } catch (err) {
      console.error("Failed to refresh analysis:", err);
    } finally {
      setIsRefreshing(false);
    }
  }

  if (charts.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">{isRefreshing ? "⏳" : "📊"}</div>
        <h3>{isRefreshing ? "AI agents are working..." : "No charts generated yet"}</h3>
        <p>
          {isRefreshing 
            ? "We're re-analyzing your data to identify better visualizations." 
            : "The AI didn't find specific trends for charts this time, or the analysis is still finishing."}
        </p>
        {sessionId && !isRefreshing && (
          <button className="btn-secondary" onClick={handleRefresh}>
            Refetch Analysis ✨
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="charts-wrapper">
      <div className="section-header">
        <h2 className="section-title">📊 Suggested Visualizations</h2>
        <span className="badge">{charts.length} charts</span>
      </div>
      <p className="section-sub">
        The AI analyzed your dataset and identified these key visualizations.
      </p>
      <div className="charts-grid">
        {charts.map((chart, i) => (
          <ChartCard key={i} chart={chart} index={i} data={chartData} />
        ))}
      </div>
    </div>
  );
}
