# Production-Ready Research Agent (Google Gemini + Tavily Search)

A streamlined, production-grade autonomous research agent powered by the official **Google Gemini API** (`google-genai`) and **Tavily Search** (`tavily-python`) for live, authoritative real-world citations.

---

## 🌟 Key Architecture & Capabilities

1. **Multi-Tool Real-World Research (`tools.py`)**:
   - 🌐 **Tavily Live Search (`tavily_search`)**: Queries live web sources, technical documentation, benchmarks, and research papers tailored for AI agents with full source URLs.
   - 📚 **Wikipedia Lookup (`search_wikipedia`)**: Queries Wikipedia's REST API for foundational encyclopedia concepts, history, and scientific background.
2. **Hard Step Limiter (`agent.py`)**:
   - Enforces a strict maximum iteration counter (`max_steps`, default: 5).
   - If reached, the agent halts tool invocation, alerts the user, and forces Gemini to synthesize the final answer strictly from evidence collected so far.
3. **Traceable In-Text Citations (`citation.py`)**:
   - Deduplicates and registers all retrieved web sources into sequential `[1]`, `[2]` citation IDs.
   - Automatically audits the final synthesis to verify in-text citations and catch hallucinations.
   - Generates an itemized reference bibliography at the end of the report.
4. **Graceful Error Handling**:
   - Catches missing API keys, HTTP timeouts, connection errors, and rate limits.
   - Returns structured observations with guidance so Gemini can pivot queries without crashing.
5. **Rich Terminal Audit Trail**:
   - Displays clear, color-coded execution logs of tool choices, arguments, observation summaries, citation integrity metrics, and formatted markdown synthesis.

---

## 🚀 Setup & Execution Guide

### 1. Activate Virtual Environment (`venv`)

#### Windows (PowerShell):
```powershell
cd "Tool-Using Research Agent"
.venv\Scripts\Activate.ps1
```

#### macOS / Linux:
```bash
cd "Tool-Using Research Agent"
source .venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure API Keys (`.env`)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Set your keys inside `.env`:
```ini
# Google Gemini API Key (Get from: https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Tavily API Key (Get from: https://tavily.com/)
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: Gemini model (default: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash
```

---

### 4. Running the Agent

#### A. Interactive Prompt:
```bash
python main.py
```

#### B. Direct Query with Custom Step Limit:
```bash
python main.py --query "What are the latest benchmarks for DeepSeek-R1 reasoning models?" --max-steps 4
```

#### C. Offline / Mock Verification (No API Keys Required):
```bash
python main.py --mock --query "Explain the architecture of Mixture of Experts"
```

#### D. Run the Automated Test Suite:
```bash
python test_agent.py
```
