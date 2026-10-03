# 🔬 Autonomous Tool-Using Research Agent

> An autonomous AI research assistant powered by **Google Gemini** and **Tavily Search** that gathers real-world empirical evidence across the web and synthesizes comprehensive, verified research reports in a strict 2-step execution budget.

---

## 📌 Project Overview
The **Autonomous Tool-Using Research Agent** is a production-ready system designed to answer complex technical, scientific, and industry research queries. Rather than relying on static parametric memory, the agent autonomously routes queries to specialized external tools—such as **Tavily Live Search** for real-time web documentation and benchmarks, and **Wikipedia API** for encyclopedic grounding—while maintaining strict execution limits and traceability.

---

## ❓ Why This Project?
While Large Language Models (LLMs) excel at language generation, deploying them for autonomous research introduces critical challenges:
- **Hallucinations & Stale Data**: Foundation models produce plausible-sounding but outdated or fictional facts when answering cutting-edge questions.
- **Infinite Runaway Loops**: Naive agentic loops frequently spiral into repetitive tool calls without converging on a final answer, draining API quotas and causing timeouts.
- **Cluttered Output & Unverifiable Claims**: Many agents clutter sentences with raw markdown links or bracketed badges like `[1]`, `[2]`, yet fail to provide authenticated source metadata.
- **Fragile Web Scraping**: Traditional web scrapers get easily blocked, suffer from rate limits, and inject noisy HTML into context windows.

### How This Solution Solves It:
- **Strict 2-Step Execution Budget**: The agent is hard-constrained to at most 2 iterations (Step 1: targeted factual retrieval; Step 2: structured synthesis). Runaway loops are mathematically impossible.
- **Tavily Agent Search**: Leverages Tavily's purpose-built API to retrieve curated, high-signal content snippets and canonical source URLs.
- **Clean Prose with Verified Resource Cards**: Inline sentence clutter (`[1]`, `[2]`) is eliminated; all verified sources are organized into dedicated, interactive cards with direct domain indicators, one-click links, and copy actions.
- **Multi-Model Resilience**: Automatically fails over between Gemini models (`gemini-flash-latest`, `gemini-3.5-flash-lite`, `gemini-3.8-flash`) if rate limits (429) or transient server overloads (503) occur.

---

## ✨ Features
- 🌐 **Dual-Tool Autonomous Routing**: Intelligently selects between **Tavily Live Web Search** (real-time news, technical documentation, benchmarks) and **Wikipedia** (historical context, foundational concepts).
- ⏱️ **Strict 2-Step Safety Guardrail**: Ensures fast responses and predictable latency by guaranteeing report delivery within 2 iterations.
- 📑 **Standardized Structured Reports**: Every synthesis follows a rigorous briefing format:
  - 📌 **Executive Summary**
  - 🔍 **Key Findings & Empirical Evidence**
  - ⚙️ **Technical Analysis & Mechanism**
  - ⚠️ **Limitations & Trade-Offs**
  - 💡 **Strategic Takeaway**
- 📚 **Interactive Resource Dashboard**: Clean card grid displaying consulted sources, domain badges, origin tool tags, and one-click URL copy.
- ⚡ **Real-Time SSE Streaming**: Live Server-Sent Events (SSE) stream the agent's thought process, tool invocations, and observations in real time.
- 🎨 **Minimalist Glassmorphic UI**: High-aesthetic dark-mode dashboard built with pure CSS and Vanilla JS, requiring no heavy frontend builds.
- 🖥️ **Dual Interface Support**: Run via interactive web UI or terminal CLI with `rich` color-coded panels.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **LLM Engine** | **Google Gemini** (`google-genai` SDK) | `gemini-flash-latest`, `gemini-3.5-flash-lite` |
| **Web Search** | **Tavily Search API** (`tavily-python`) | Agent-optimized real-time web retrieval |
| **Encyclopedia** | **Wikipedia REST API** (`requests`, `BeautifulSoup4`) | Foundational scientific & conceptual lookup |
| **Backend API** | **FastAPI** + **Uvicorn** | High-performance asynchronous API server |
| **Streaming** | **Server-Sent Events (SSE)** | Low-latency step-by-step trace delivery |
| **Frontend** | **Vanilla HTML5, CSS3, JavaScript** | Modern dark-mode UI with `marked.js` markdown rendering |
| **CLI / Terminal** | **Rich** + **Python-Dotenv** | Formatted terminal tables, audit panels, and env management |

---

## 🚀 Setup & Installation Guide

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- An API Key from [Google AI Studio](https://aistudio.google.com/).
- An API Key from [Tavily AI](https://tavily.com/).

---

### 2. Clone the Repository
```bash
git clone https://github.com/OmPatel9019/Tools-Using-ResearchAgent.git
cd Tools-Using-ResearchAgent
```

---

### 3. Create & Activate a Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 4. Install Dependencies
```bash
cd "Tool-Using Research Agent"
pip install -r requirements.txt
```

---

### 5. Configure Environment Variables
Copy the `.env.example` template to `.env`:
```bash
cp .env.example .env
```

Open `.env` and insert your API keys:
```ini
# Google Gemini API Key (https://aistudio.google.com/)
GEMINI_API_KEY="your-google-gemini-api-key"

# Tavily Search API Key (https://tavily.com/)
TAVILY_API_KEY="your-tavily-api-key"

# Model Selection (Recommended: gemini-flash-latest)
GEMINI_MODEL=gemini-flash-latest
```

---

### 6. Run the Application

#### Option A: Launch the Web UI (Recommended)
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

#### Option B: Run in Terminal (CLI Mode)
```bash
# Interactive mode
python main.py

# Direct query mode
python main.py --query "What is FlashAttention and how does it optimize GPU memory?"

# Offline / Mock mode (no API keys required)
python main.py --mock --query "Explain Quantum Error Correction"
```

#### Option C: Run Test Suite
```bash
python test_agent.py
```

---

## 📂 Project Structure
```
Tools-Using-ResearchAgent/
├── .gitignore                      
├── README.md                      
└── Tool-Using Research Agent/
    ├── .env                       
    ├── .env.example                
    ├── requirements.txt            
    ├── agent.py                   
    ├── server.py                   
    ├── tools.py                    
    ├── citation.py                 
    ├── test_agent.py               
    ├── main.py                   
    └── static/
        ├── index.html             
        ├── style.css               
        └── app.js                  
```

---

