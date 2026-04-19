# 🤖 Analyst AI

> A multi-agent AI-powered data analysis platform built with **FastAPI**, **LangGraph**, and **React Router v7** — turning raw CSV files into deep insights, interactive charts, and intelligent Q&A.

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React%2019-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=flat-square&logo=google)](https://ai.google.dev/)
[![Orchestration](https://img.shields.io/badge/Orchestration-LangGraph-1C1C1C?style=flat-square)](https://www.langchain.com/langgraph)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## ✨ Features

- 📤 **CSV Upload** — Upload any dataset or use the built-in sample data (Walmart.csv)
- 🧹 **Automated Data Cleaning** — AI-powered null handling, type inference, and outlier detection
- 📊 **EDA & Insights** — Exploratory data analysis with AI-generated business insights
- 📈 **Interactive Charts** — Bar, line, scatter, histogram, and pie charts via Recharts
- 💬 **Natural Language Q&A** — Ask questions about your data in plain English
- 🔀 **Data Manipulation** — AI-driven data transformation based on user intent
- 📝 **Report Generation** — Auto-generated markdown reports summarizing the analysis
- 📥 **CSV Export** — Download the cleaned dataset at any time
- 📱 **Mobile Responsive** — Fully optimized across all screen sizes

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                       │
│   Upload → Insights → Charts → Chat → Report            │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (Axios)
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                         │
│   /upload  /analyze  /query  /report  /export           │
└────────────────────────┬────────────────────────────────┘
                         │ LangGraph Orchestration
┌────────────────────────▼────────────────────────────────┐
│                  Multi-Agent Pipeline                    │
│                                                         │
│  Data Cleaner → EDA Analyzer → Insight Generator        │
│       → Visualization Agent → Report Generator          │
│                                                         │
│  Query Pipeline: QA Agent ──→ Data Manipulator          │
└─────────────────────────────────────────────────────────┘
                         │
              Google Gemini LLM (per-agent API keys)
```

### 🤖 AI Agent Breakdown

| Agent | Responsibility |
|-------|---------------|
| `data_cleaner` | Handles missing values, type casting, deduplication |
| `eda_analyzer` | Computes statistics, distributions, and correlations |
| `insight_generator` | Generates natural-language business insights |
| `visualization_agent` | Recommends and prepares chart configurations |
| `report_generator` | Compiles a full markdown analysis report |
| `qa_agent` | Classifies user queries (Q&A vs. manipulation intent) |
| `data_manipulator` | Applies AI-driven transformations to the dataset |

---

## 🗂️ Project Structure

```
Analyst_AI/
├── Backend/
│   ├── agents/              # Individual AI agents
│   │   ├── data_cleaner.py
│   │   ├── eda_analyzer.py
│   │   ├── insight_generator.py
│   │   ├── visualization_agent.py
│   │   ├── report_generator.py
│   │   ├── qa_agent.py
│   │   └── data_manipulator.py
│   ├── graph/
│   │   └── workflow.py      # LangGraph pipelines (analysis + query)
│   ├── routers/             # FastAPI route handlers
│   │   ├── upload.py
│   │   ├── analyze.py
│   │   ├── query.py
│   │   ├── report.py
│   │   └── export.py
│   ├── state/               # Shared agent state (AnalystState)
│   ├── memory/              # In-memory session storage
│   ├── utils/               # Helper utilities
│   ├── config.py            # API key management
│   ├── main.py              # FastAPI app entry point
│   └── requirements.txt
│
└── Frontend/
    ├── app/
    │   ├── components/      # UI section components
    │   │   ├── UploadSection.tsx
    │   │   ├── InsightsSection.tsx
    │   │   ├── ChartsSection.tsx
    │   │   ├── QuerySection.tsx
    │   │   └── ReportSection.tsx
    │   ├── context/
    │   │   └── AnalystContext.tsx   # Global state management
    │   ├── lib/
    │   │   └── api.ts               # Centralized Axios API client
    │   ├── routes/                  # React Router v7 pages
    │   └── app.css                  # Global styles
    ├── package.json
    └── vite.config.ts
```

---

## 🚀 Getting Started

### Prerequisites

- Python `3.12+`
- Node.js `18+`
- Google Gemini API Key(s) — [Get one here](https://ai.google.dev/)

---

### 🔧 Backend Setup

```bash
# Navigate to the backend directory
cd Backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your environment file
cp .env.example .env
```

Edit `.env` and add your Gemini API keys:

```env
# Assign unique keys per agent (to avoid rate-limiting)
GEMINI_API_KEY1=your_key_for_data_cleaner
GEMINI_API_KEY2=your_key_for_visualization
GEMINI_API_KEY3=your_key_for_insights
GEMINI_API_KEY4=your_key_for_report
GEMINI_API_KEY5=your_key_for_qa
GEMINI_API_KEY6=your_key_for_manipulator
```

> **Tip:** You can use the same key for all agents during development (`GEMINI_API_KEY1=...` through `GEMINI_API_KEY6=...`). Using separate keys in production prevents `429 Too Many Requests` errors from concurrent agent calls.

```bash
# Start the development server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

### 🎨 Frontend Setup

```bash
# Navigate to the frontend directory
cd Frontend

# Install dependencies
npm install

# Create your environment file
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

```bash
# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a CSV file |
| `POST` | `/analyze` | Trigger the full analysis pipeline |
| `POST` | `/query` | Ask a natural language question |
| `GET` | `/report` | Retrieve the generated analysis report |
| `GET` | `/export` | Download the cleaned CSV |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | REST API framework |
| [LangGraph](https://www.langchain.com/langgraph) | Multi-agent orchestration |
| [LangChain Google GenAI](https://pypi.org/project/langchain-google-genai/) | Gemini LLM integration |
| [Pandas](https://pandas.pydata.org/) | Data manipulation & EDA |
| [Pydantic](https://docs.pydantic.dev/) | Data validation & schemas |
| [Uvicorn](https://www.uvicorn.org/) / [Gunicorn](https://gunicorn.org/) | ASGI server |

### Frontend
| Technology | Purpose |
|-----------|---------|
| [React 19](https://react.dev/) | UI framework |
| [React Router v7](https://reactrouter.com/) | File-based routing (SSR-ready) |
| [Recharts](https://recharts.org/) | Interactive data visualization |
| [Axios](https://axios-http.com/) | HTTP client |
| [TypeScript](https://www.typescriptlang.org/) | Type safety |
| [Vite](https://vitejs.dev/) | Build tool |
| [Tailwind CSS v4](https://tailwindcss.com/) | Utility-first styling |

---

## 🌊 Analysis Workflow

```
1. Upload CSV
      ↓
2. Data Cleaner      ← Fixes nulls, corrects types, removes duplicates
      ↓
3. EDA Analyzer      ← Computes stats, correlations, distributions
      ↓
4. Insight Generator ← AI generates key business takeaways
      ↓
5. Visualization     ← AI recommends optimal chart types & configs
      ↓
6. Report Generator  ← Compiles a full markdown analysis report
```

**Query Flow (independent):**
```
User Question → QA Agent → classify intent
                              ├── "question"     → answer directly
                              └── "manipulation" → Data Manipulator → updated dataset
```

---

## 🌐 Deployment

The project is deployed on:
- **Frontend**: [analystai.kaustubh.codes](https://analystai.kaustubh.codes) 
- **Backend**: Hosted on [Render](https://render.com/) (Python 3.12.3)

For custom deployment, the frontend includes a `Dockerfile` for containerized builds.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ by <a href="https://github.com/Kaustubh0505">Kaustubh</a></p>
