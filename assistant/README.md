# AI Chat Assistant

A LangGraph-based AI agent that powers the chat widget on the homepage. It answers visitor questions about Van-Tuan Le using a knowledge base built from the site content, and can send contact emails on behalf of visitors.

## Architecture

```
Frontend (Jekyll)          Backend (FastAPI + LangGraph)
┌─────────────┐            ┌──────────────────────────────┐
│ Chat Widget │──POST───►  │ /api/chat                    │
│ (JS/CSS)    │  /api/chat │   └─► LangGraph ReAct Agent  │
└─────────────┘            │         ├─ send_email         │
                           │         ├─ refresh_knowledge  │
                           │         └─ get_contact_info   │
                           │                               │
                           │ LLM Providers:                │
                           │   OpenAI / Gemini / NVIDIA /  │
                           │   Local Ollama                │
                           └──────────────────────────────┘
```

## Quick Start

### 1. Create a virtual environment

```bash
cd assistant
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your values. At minimum you need:

- **LLM_PROVIDER** and its corresponding API key
- **SMTP settings** (if you want the email tool to work)

### 4. Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

The server will be available at `http://localhost:8001`.

Verify it's running:

```bash
curl http://localhost:8001/health
# {"status":"ok","type":"langgraph-agent"}
```

## LLM Providers

Set `LLM_PROVIDER` in `.env` to one of:

| Provider | Value | Required Env Vars |
|----------|-------|-------------------|
| Google Gemini | `gemini` | `GEMINI_API_KEY`, `GEMINI_MODEL` |
| OpenAI | `openai` | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| NVIDIA Inference API | `nvidia` | `NVIDIA_API_KEY`, `NVIDIA_MODEL` |
| Local Ollama | `local` | `LOCAL_LLM_URL`, `LOCAL_LLM_MODEL` |

### Using Ollama (local, free)

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3.2`
3. Set in `.env`:
   ```
   LLM_PROVIDER=local
   LOCAL_LLM_URL=http://localhost:11434
   LOCAL_LLM_MODEL=llama3.2
   ```

### Using NVIDIA Inference API

1. Get an API key from https://build.nvidia.com
2. Set in `.env`:
   ```
   LLM_PROVIDER=nvidia
   NVIDIA_API_KEY=your-key
   NVIDIA_MODEL=nvidia/openai/gpt-oss-20b
   ```

## Agent Tools

The agent has three tools it can call autonomously:

| Tool | Description |
|------|-------------|
| `send_email` | Sends an email to the site owner on behalf of a visitor. Requires SMTP configuration. |
| `refresh_knowledge` | Re-reads `_pages/about.md` and `_config.yml` to regenerate `knowledge.md`. |
| `get_contact_info` | Returns accurate contact details from the knowledge base. |

## Email Setup (Gmail)

To enable the `send_email` tool with Gmail:

1. Enable 2-Step Verification on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Set in `.env`:
   ```
   EMAIL_TO=your-email@gmail.com
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   ```

## Knowledge Base

`knowledge.md` contains all the information the agent uses to answer questions. It is generated from the homepage source files.

### Auto-sync (CI)

The GitHub Actions workflow `.github/workflows/sync-knowledge.yml` automatically regenerates `knowledge.md` whenever `_pages/about.md` or `_config.yml` is pushed to `main`.

### Manual sync

```bash
python sync_knowledge.py
```

## File Structure

```
assistant/
├── main.py              # FastAPI server entry point
├── agent.py             # LangGraph ReAct agent
├── llm.py               # LLM provider factory
├── tools.py             # Agent tools (email, refresh, contact)
├── sync_knowledge.py    # Script to regenerate knowledge.md
├── knowledge.md         # Generated knowledge base
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Running with the Homepage

1. Start the assistant backend (this server) on port 8001
2. Set `CHAT_BACKEND_URL=http://localhost:8001` in the root `.env`
3. Start the Jekyll site: `bash run_server.sh`
4. Open http://localhost:4000 and click the chat bubble
