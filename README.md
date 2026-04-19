# Multi-Agent Research System

A small **multi-step research pipeline** that combines web search, targeted page scraping, report generation, and an LLM “critic” pass. It exposes a **FastAPI** service and can also be run as a **CLI** script.

## What it does

1. **Search agent** — Uses [Tavily](https://tavily.com/) to find recent pages (titles, URLs, snippets) for your topic.
2. **Reader agent** — Chooses a relevant URL from the search summary and **scrapes** the page for deeper text (via `requests` + BeautifulSoup).
3. **Writer** — Synthesizes a structured report from search results + scraped content.
4. **Critic** — Reviews the report and returns a score, strengths, improvements, and a one-line verdict.

The shared model is **Google Gemini** (`gemini-3-flash-preview`) via `langchain-google-genai`, with temperature `0` for more deterministic outputs.

## Requirements

- **Python** — This repo’s `pyproject.toml` targets `>=3.14`. Use that version if you install with `uv`/`pip` against the project file; otherwise align your environment with whatever you use to resolve dependencies.
- **API keys**
  - **`TAVILY_API_KEY`** — Required for web search (`tools.py`).
  - **Google Gemini API key** — Required for all LLM calls. `langchain-google-genai` accepts **`GOOGLE_API_KEY`** (preferred) or **`GEMINI_API_KEY`** as a fallback.

Create a `.env` file in the project root (it is gitignored):

```env
TAVILY_API_KEY=your_tavily_key
GOOGLE_API_KEY=your_google_generative_ai_key
# or: GEMINI_API_KEY=...
```

## Installation

### Option A — `pyproject.toml` (recommended for this repo)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -e .
```

If the project is not packaged as an installable module, use:

```bash
pip install -r requirements.txt
pip install fastapi uvicorn langchain-google-genai
```

(`requirements.txt` in this repo is broader than the minimal runtime; `pyproject.toml` lists the dependencies used for the app and agents.)

### Option B — `requirements.txt` only

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Ensure **`langchain-google-genai`**, **`fastapi`**, and **`uvicorn`** are installed if you run the HTTP API.

## How to run

### HTTP API (FastAPI)

```bash
python main.py
```

- Serves on **`http://0.0.0.0:8000`** (all interfaces).
- Interactive docs: **`http://localhost:8000/docs`**.

**Endpoint:** `POST /research`

**Request body (JSON):**

```json
{ "topic": "Your research topic" }
```

**Response (JSON):**

| Field | Description |
|--------|-------------|
| `report` | Full drafted report (introduction, findings, conclusion, sources). |
| `feedback` | Critic output (score, strengths, areas to improve, verdict). |
| `scraped_content` | Text extracted from the URL the reader agent chose. |

Research can take on the order of **15–30+ seconds** per request; the route is synchronous. For production, consider background jobs, streaming, or a queue.

### CLI (pipeline only)

```bash
python pipeline.py
```

You will be prompted for a topic. The same four steps run with console logging.

## Project layout

| File | Role |
|------|------|
| `main.py` | FastAPI app: validates input, runs `run_research_pipeline`, returns JSON. |
| `pipeline.py` | Orchestrates search → read → write → critic; shared entry for API and CLI. |
| `agents.py` | Gemini model, LangChain `create_agent` for search/reader, prompt chains for writer/critic. |
| `tools.py` | `web_search` (Tavily), `scrape_url` (HTTP + BeautifulSoup, truncated text). |

## Design notes

- **Agents** (`search_agent`, `reader_agent`) are LangChain agents with tools; **writer** and **critic** are simple **LCEL** chains (`prompt | llm | StrOutputParser()`).
- Search snippets passed to the reader are **truncated** (first ~800 characters of the search string in `pipeline.py`) to limit context size.
- Scraped HTML is cleaned (scripts, styles, nav, footer removed) and text is **capped at 3000 characters** per scrape.
- Scraping uses a short **timeout** (8s) and a browser-like `User-Agent`; some sites may still block or return errors—those surface in `scraped_content` or tool messages.

## Troubleshooting

- **`TAVILY_API_KEY` missing or invalid** — Search fails; check `.env` and Tavily dashboard.
- **Gemini / Google errors** — Confirm `GOOGLE_API_KEY` or `GEMINI_API_KEY` and model access for `gemini-3-flash-preview` in your Google AI project.
- **Empty or poor reports** — Often tied to weak search results, scrape failures, or strict site policies; inspect `scraped_content` in the API response.

## License

Add a license file if you intend to distribute this project.
