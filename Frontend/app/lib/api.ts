import axios from "axios";

const BASE_URL = import.meta.env.VITE_BACKEND_URL ?? "http://127.0.0.1:8000";

export const api = axios.create({ baseURL: BASE_URL });

// 1. Upload CSV → { message, session_id, rows, columns[] }
export async function uploadCSV(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

// 2. Run full AI analysis pipeline → { insights[], charts[], eda_summary{} }
export async function analyzeData(session_id = "default") {
  const res = await api.post(`/analyze?session_id=${session_id}`);
  return res.data;
}

// 3. Q&A or data manipulation → { answer, intent, manipulation_plan, download_available }
export async function queryData(question: string, session_id = "default") {
  const res = await api.post("/query", { question, session_id });
  return res.data;
}

// 4. Fetch full analyst report → { report }
export async function fetchReport(session_id = "default") {
  const res = await api.get(`/report?session_id=${session_id}`);
  return res.data;
}

// 5. Download cleaned/manipulated CSV
export function getExportURL(session_id = "default") {
  return `${BASE_URL}/export?session_id=${session_id}`;
}
