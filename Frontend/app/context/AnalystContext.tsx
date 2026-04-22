import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

export interface ChartSpec {
  type: "bar" | "line" | "scatter" | "histogram" | "pie" | "heatmap";
  x: string;
  y: string;
  title: string;
}

export interface EdaSummary {
  shape?: { rows: number; cols: number };
  columns?: string[];
  correlation?: Record<string, Record<string, number>>;
}

interface AnalystState {
  sessionId: string | null;
  columns: string[];
  rows: number | null;
  insights: string[];
  charts: any[]; // Changed: Now stores {spec, data}
  edaSummary: EdaSummary | null;
  report: string | null;
  downloadAvailable: boolean;
  chartData: any[];
  setSessionId: (id: string) => void;
  setColumns: (cols: string[]) => void;
  setRows: (n: number) => void;
  setAnalysisResult: (result: any) => void;
  setReport: (r: string) => void;
  setDownloadAvailable: (v: boolean) => void;
}

const AnalystContext = createContext<AnalystState | null>(null);

export function AnalystProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<number | null>(null);
  const [insights, setInsights] = useState<string[]>([]);
  const [charts, setCharts] = useState<any[]>([]);
  const [edaSummary, setEdaSummary] = useState<EdaSummary | null>(null);
  const [report, setReport] = useState<string | null>(null);
  const [downloadAvailable, setDownloadAvailable] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);

  function setAnalysisResult(result: any) {
    setInsights(result.insights ?? []);
    setCharts(result.aggregated_charts ?? []);
    setEdaSummary(result.eda_summary ?? null);
    setChartData(result.chart_data ?? []);
    setDownloadAvailable(true);
  }

  return (
    <AnalystContext.Provider
      value={{
        sessionId,
        columns,
        rows,
        insights,
        charts,
        edaSummary,
        report,
        downloadAvailable,
        chartData,
        setSessionId,
        setColumns,
        setRows,
        setAnalysisResult,
        setReport,
        setDownloadAvailable,
      }}
    >
      {children}
    </AnalystContext.Provider>
  );
}

export function useAnalyst() {
  const ctx = useContext(AnalystContext);
  if (!ctx) throw new Error("useAnalyst must be used inside <AnalystProvider>");
  return ctx;
}
