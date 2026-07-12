# Cortex: Industrial RAG Platform

**Cortex** is a production-grade retrieval-augmented generation (RAG) system designed for complex industrial document intelligence. It ingests technical documents, constructs a rich Knowledge Graph, and exposes a multi-agent reasoning layer that answers natural language queries with full provenance and citation support.

**Live Frontend Demo**: [https://cortex-search-ai.vercel.app](https://cortex-search-ai.vercel.app)

---

## 🚀 AMD Compute Usage & ML Architecture

Cortex was designed specifically to leverage high-performance GPU compute. All heavy machine learning workloads are entirely offloaded to the **AMD AI Notebooks** platform running on **ROCm 7.2**.

Our `cortex_unified_notebook.ipynb` (AMD Hackathon Edition) runs a Unified ML Gateway that exposes:
1. **vLLM (ROCm-optimized)**: Serving `Qwen/Qwen2.5-7B-Instruct` for all generative tasks, agent reasoning, and graph extraction.
2. **IBM Docling**: Performing heavy layout-aware parsing, OCR, and table structure recognition on PDFs.
3. **FastEmbed**: Generating `BAAI/bge-base-en-v1.5` embeddings (768-dim) for dense vector retrieval.

This single AMD GPU node exposes these services via an Ngrok tunnel (`https://entree-antiquely-rotting.ngrok-free.dev`), allowing our lightweight backend to securely communicate with the powerhouse ML models.

---

## 🛠️ Main Code Paths & Implementation Details

Our repository is designed for easy review. Here are the core implementation paths:

- **Knowledge Graph Ingestion Pipeline**: `backend/ingestion_worker/`
  - Explains how we use Docling and LLMs to extract entities/relationships from PDFs into Neo4j.
- **Hybrid Retrieval Pipeline (P2)**: `backend/app/retrieval/`
  - Explains our 3-way retrieval (Dense, Lexical, Graph Traversal) fused using Reciprocal Rank Fusion (RRF).
- **Multi-Agent Reasoning Layer (P3)**: `backend/app/agents/`
  - Explains our LangGraph-based Copilot, Supervisor, and specialized Workers (Asset, Diagnose, Comply).

---

## 🏗️ Architecture & External Services

Cortex uses a modern, scalable microservices architecture:

| Component        | Technology & External Service                                   |
| ---------------- | --------------------------------------------------------------- |
| **Frontend**     | Next.js 16, React 19, Tailwind CSS 4 (Deployed on **Vercel**)     |
| **Backend API**  | FastAPI (Async, Python 3.11+)                                   |
| **Metadata DB**  | PostgreSQL (Neon DB) - Stores document metadata and status      |
| **Vector Store** | Qdrant Cloud - Stores dense chunk embeddings                    |
| **Graph Store**  | Neo4j AuraDB - Stores the LLM-extracted Knowledge Graph         |
| **Task Queue**   | Redis (Upstash) & Python RQ - Handles asynchronous ingestion    |
| **ML Gateway**   | AMD AI Notebooks (ROCm + vLLM + Docling + FastEmbed)            |

---

## 💻 Setup Instructions (Running Locally)

To run the full project locally, follow these steps:

### 1. Start External Infrastructure (Docker)
We use Docker Compose to spin up local instances of our databases.
```bash
docker compose up -d
```
*(This provisions local PostgreSQL, Redis, Qdrant, and Neo4j)*

### 2. Launch the AMD ML Gateway
1. Upload `cortex_unified_notebook.ipynb` to the AMD AI Notebooks platform.
2. Add your Ngrok auth token in the notebook configuration block.
3. Run all cells to start vLLM, FastEmbed, and Docling.
4. Copy the generated Ngrok public URL (e.g., `https://your-url.ngrok-free.dev`).

### 3. Backend Setup
```bash
cd backend
cp .env.example .env
```
Update the `.env` file with your ML Gateway URL:
```env
REMOTE_PARSER_URL=https://your-url.ngrok-free.dev/parse
EMBEDDING_MODEL_ENDPOINT=https://your-url.ngrok-free.dev/v1
LLM_BASE_URL=https://your-url.ngrok-free.dev/v1
```
Install dependencies and run the server:
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
alembic upgrade head
uv run uvicorn backend.fabric_api.main:app --reload --port 8000
```

### 4. Run the Ingestion Worker
In a separate terminal (with the backend `.venv` activated):
```bash
cd backend
uv run python -m backend.ingestion_worker.main
```

### 5. Frontend Setup
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
The frontend will be available at `http://localhost:3000`.

---

## 🔒 Original Work & Security Posture
- **Zero-Trust Defaults**: We employ robust Cypher injection mitigation by sanitizing all LLM-derived node and relationship labels via regex `[a-z0-9_]`.
- **Resilient Workers**: Custom DLQ Auto-Recovery daemons that poll the AMD ML Gateway for liveliness before requeuing failed ingestion jobs.

## License
MIT License. See [LICENSE](LICENSE) for details.