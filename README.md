# Text-to-SQL Agent

Natural language → SQL → Results. Powered by Claude + ChromaDB.

**Live Demo:** https://text-to-sql-agent-4m43.onrender.com

## Architecture

User Question → [RAG] Schema Retrieval → [LLM] SQL Generation → [Executor] Run Query → [Self-Correction] Auto-fix errors → Results

## Tech Stack

Python · Claude API · ChromaDB · SQLite · FastAPI · RAG

## Modules

- `schema_rag.py` — Semantic schema retrieval using ChromaDB embeddings
- `sql_generator.py` — Prompt engineering + Claude API call
- `sql_executor.py` — SQL execution with structured error handling
- `self_corrector.py` — Multi-turn self-correction loop
- `server.py` — FastAPI backend
- `startup.py` — Database + ChromaDB initialization

## Setup

```bash
git clone https://github.com/abhigyanpal1/text-to-sql-agent
cd text-to-sql-agent
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key" > .env
python startup.py
python server.py
```

Open `index.html` in your browser.
