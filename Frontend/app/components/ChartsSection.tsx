import { useAnalyst } from "../context/AnalystContext";
import type { ChartSpec } from "../context/AnalystContext";
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

function ChartCard({ chart, index }: { chart: ChartSpec; index: number }) {
  // Generate illustrative placeholder data based on chart spec
  const placeholderData = Array.from({ length: 7 }, (_, i) => ({
    [chart.x || "x"]: `Item ${i + 1}`,
    [chart.y || "y"]: Math.round(Math.random() * 80 + 20),
  }));

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
            <BarChart data={placeholderData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey={chart.x || "x"} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0" }}
              />
              <Bar dataKey={chart.y || "y"} fill={color} radius={[4, 4, 0, 0]} />
            </BarChart>
          ) : chart.type === "line" ? (
            <LineChart data={placeholderData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
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
                data={placeholderData}
                dataKey={chart.y || "y"}
                nameKey={chart.x || "x"}
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {placeholderData.map((_, i) => (
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
              <Scatter data={placeholderData} fill={color} />
            </ScatterChart>
          ) : (
            // Fallback: bar
            <BarChart data={placeholderData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
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
        ℹ️ Charts are rendered with illustrative data. When your dataset rows are available via the backend, real data will populate here.
      </p>
    </div>
  );
}

export function ChartsSection() {
  const { charts } = useAnalyst();

  if (charts.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📊</div>
        <h3>No charts yet</h3>
        <p>Upload and analyze a CSV file — the AI will suggest the best visualizations for your data.</p>
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
        The AI analyzed your dataset and recommends these chart types. Add a <code>/data</code> endpoint to your backend to render with real data.
      </p>
      <div className="charts-grid">
        {charts.map((chart, i) => (
          <ChartCard key={i} chart={chart} index={i} />
        ))}
      </div>
    </div>
  );
}
