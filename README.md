# 🔍 Influencer Intel — Content Intelligence & Fact-Checking Tool

## What This Tool Does
- **Batch-analyzes** influencer content (PDFs, DOCX, URLs, raw text) against a campaign brief using LLMs, extracting intent, sentiment, entities, and campaign alignment score
- **Fact-checks** every verifiable claim in the content against live web sources via Tavily search, returning verdicts (TRUE / FALSE / MISLEADING / UNVERIFIABLE)
- **Exports** a color-coded Excel report (3 sheets) or flat CSV for further processing — built for non-technical analysts handling hundreds of content pieces

---

## Setup Instructions

### 1. Clone / download the project
```bash
cd influencer-intel
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
> Requires Python 3.9+

### 3. Add API keys (optional — can also enter in sidebar at runtime)
Edit `.streamlit/secrets.toml`:
```toml
[api_keys]
GEMINI_API_KEY = "your-gemini-key"
GROQ_API_KEY   = "your-groq-key"
TAVILY_API_KEY = "your-tavily-key"
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## How to Use

1. **Fill the Campaign Brief** in the left sidebar — theme, required message, key people, purpose, audience
2. **Enter API keys** in the sidebar (or pre-fill in `secrets.toml`)
3. **Upload files** (PDF / DOCX / TXT), paste URLs, or paste raw text in the **📥 Input Content** tab — or click **Load Demo Content** to try instantly
4. Click **🚀 Run Analysis** — watch the live progress through extraction → analysis → fact-checking
5. Review results in **📊 Results Dashboard**, then export via **📤 Export**

---

## API Keys Needed

| Key | Purpose | Where to get |
|-----|---------|--------------|
| **Gemini API Key** | Primary LLM (analysis + fact-check verdicts) | [Google AI Studio](https://aistudio.google.com/app/apikey) — free tier available |
| **Groq API Key** | Fallback LLM if Gemini fails | [console.groq.com](https://console.groq.com) — free tier available |
| **Tavily API Key** | Live web search for fact-checking | [tavily.com](https://tavily.com) — free tier: 1000 searches/month |

> The tool works without Tavily (fact-checking is skipped) and without Groq (falls back gracefully). Only one LLM key is required.

---

## Deployment on Streamlit Cloud

1. Push this project to a **GitHub repository** (ensure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your repo → set main file to `app.py`
4. In **Advanced settings → Secrets**, paste your secrets in TOML format:
   ```toml
   [api_keys]
   GEMINI_API_KEY = "..."
   GROQ_API_KEY   = "..."
   TAVILY_API_KEY = "..."
   ```
5. Click **Deploy** — the app will be live at `https://<your-app>.streamlit.app`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      app.py (UI)                        │
│  Sidebar: Campaign Brief + API Keys + Settings          │
│  Tab 1: File/URL/Text Input → Run Analysis button       │
│  Tab 2: Results Dashboard (metrics, table, expanders)   │
│  Tab 3: Export (Excel + CSV download)                   │
└────────┬───────────────────────────────────────────────-┘
         │
         ▼
┌────────────────────┐    ┌─────────────────────────────┐
│  extractor.py      │    │  llm_client.py              │
│  PDF → pdfplumber  │    │  Gemini (primary)           │
│  DOCX → python-docx│    │    ↓ fallback on error      │
│  URL → newspaper3k │    │  Groq llama-3.1-70b         │
│  Text → cleanup    │    │  temperature=0.1 always     │
└────────┬───────────┘    └──────────────┬──────────────┘
         │                               │
         ▼                               ▼
┌────────────────────┐    ┌─────────────────────────────┐
│  analyzer.py       │───▶│  factchecker.py             │
│  LLM prompt →      │    │  Tavily search (3 results)  │
│  JSON: narrative,  │    │  LLM verdict prompt →       │
│  intent, entities, │    │  TRUE/FALSE/MISLEADING/     │
│  campaign_fit,     │    │  PARTIALLY_TRUE/UNVERIFIABLE│
│  factual_claims    │    └──────────────┬──────────────┘
└────────┬───────────┘                   │
         └───────────────┬───────────────┘
                         ▼
              ┌──────────────────────┐
              │  exporter.py         │
              │  Excel: 3 sheets,    │
              │  color-coded cells   │
              │  CSV: flat rows      │
              └──────────────────────┘
```
