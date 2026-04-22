import { useState, useMemo } from "react";
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

function CorrelationHeatmap({ correlation }: { correlation: Record<string, Record<string, number>> }) {
  const cols = Object.keys(correlation);
  if (cols.length === 0) return <div className="chat-empty">No correlation data available</div>;

  return (
    <div style={{ overflowX: "auto", paddingBottom: "10px" }}>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: "11px" }}>
        <thead>
          <tr>
            <th style={{ padding: "4px" }}></th>
            {cols.map((col) => (
              <th key={col} style={{ padding: "4px", textAlign: "center", transform: "rotate(-45deg)", height: "60px", whiteSpace: "nowrap", borderBottom: "1px solid #e2e8f0" }}>
                {col.length > 12 ? col.substring(0, 10) + ".." : col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cols.map((rowCol) => (
            <tr key={rowCol}>
              <td style={{ padding: "4px", fontWeight: "bold", borderRight: "1px solid #e2e8f0" }}>{rowCol}</td>
              {cols.map((colCol) => {
                const val = correlation[rowCol][colCol] ?? 0;
                // Color scale: Red (-1) -> White (0) -> Blue (1)
                const opacity = Math.abs(val);
                const color = val > 0 ? `rgba(99, 102, 241, ${opacity})` : `rgba(239, 68, 68, ${opacity})`;
                return (
                  <td
                    key={colCol}
                    title={`${rowCol} vs ${colCol}: ${val.toFixed(3)}`}
                    style={{
                      background: color,
                      width: "30px",
                      height: "30px",
                      border: "1px solid #f1f5f9",
                      textAlign: "center",
                      color: opacity > 0.5 ? "white" : "inherit",
                    }}
                  >
                    {val.toFixed(2)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ChartCard({ chartObj, index }: { chartObj: any; index: number }) {
  const { edaSummary } = useAnalyst();
  const chart = chartObj.spec;
  const data = chartObj.data;
  const color = COLORS[index % COLORS.length];

  // Data should already be pre-aggregated from the backend Aggregator Agent
  const displayData = data;

  return (
    <div className="chart-card" style={{ animationDelay: `${index * 80}ms` }}>
      <div className="chart-card-header">
        <div>
          <h3 className="chart-title">{chart.title}</h3>
          <div className="chart-meta">
            <span className="badge">{CHART_TYPE_LABELS[chart.type] ?? chart.type}</span>
            {chart.x && <span className="tag tag-dim">X: {chart.x}</span>}
            {chart.y && <span className="tag tag-dim">Y: {chart.y}</span>}
          </div>
        </div>
      </div>

      <div className="chart-canvas">
        {chart.type === "heatmap" ? (
          <CorrelationHeatmap correlation={edaSummary?.correlation ?? {}} />
        ) : (
          <ResponsiveContainer width="100%" height={chart.type === "pie" ? 280 : 220}>
            {chart.type === "bar" || chart.type === "histogram" ? (
              <BarChart data={displayData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                <XAxis dataKey={chart.type === "histogram" ? "label" : (chart.x || "x")} tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, color: "#0f172a", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                />
                <Bar dataKey={chart.type === "histogram" ? "count" : (chart.y || "y")} fill={color} radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : chart.type === "line" ? (
              <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                <XAxis dataKey={chart.x || "x"} tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, color: "#0f172a", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
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
                  data={displayData}
                  dataKey={chart.y || "y"}
                  nameKey={chart.x || "x"}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={2}
                  label={({ percent }: any) => `${((percent ?? 0) * 100).toFixed(0)}%`}
                >
                  {displayData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="rgba(255,255,255,0.2)" />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, color: "#0f172a", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
              </PieChart>
            ) : chart.type === "scatter" ? (
              <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                <XAxis dataKey={chart.x || "x"} name={chart.x} tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis dataKey={chart.y || "y"} name={chart.y} tick={{ fill: "#64748b", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, color: "#0f172a", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                  cursor={{ strokeDasharray: "3 3" }}
                />
                <Scatter data={data} fill={color} />
              </ScatterChart>
            ) : (
              // Fallback: bar
              <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                <XAxis dataKey={chart.x || "x"} tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, color: "#0f172a", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                />
                <Bar dataKey={chart.y || "y"} fill={color} radius={[4, 4, 0, 0]} />
              </BarChart>
            )}
          </ResponsiveContainer>
        )}
      </div>

      <p className="chart-note">
        ℹ️ {chart.type === "heatmap" ? "Showing full correlation matrix between all numeric variables." : "Visualizing pre-aggregated trends using the full dataset."}
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
        {charts.map((chartObj, i) => (
          <ChartCard key={i} chartObj={chartObj} index={i} />
        ))}
      </div>
    </div>
  );
}
