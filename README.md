<div align="center">

![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)
![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)
![AMD ROCm](https://img.shields.io/badge/AMD-ROCm-ed1c24.svg)
![vLLM](https://img.shields.io/badge/vLLM-0.16.0-blueviolet.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-orange.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph-4581c3.svg)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector-ff5252.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)

# Cortex

> **AI Operating System for Industrial Knowledge**

Turn scattered industrial documents into a searchable knowledge graph and talk to them using a multi-agent AI copilot with complete citations.

 **AMD Developer Hackathon 2026 – Unicorn Track**

 **Live Demo:** [https://cortex-search-ai.vercel.app](https://cortex-search-ai.vercel.app)  
 **Demo Video:** *(link)*  
 **Pitch Deck:** *(link)*

</div>

---

##  Why Cortex?

Traditional RAG retrieves text.  
**Cortex retrieves knowledge.**

We combine:
- **Knowledge Graphs**
- **Hybrid Retrieval**
- **Multi-Agent Reasoning**

To answer complex questions that no single document contains.

---

##  Screenshots

*(Replace with actual screenshots before submission)*

| Home Page / Graph Explorer | Document Upload |
| :---: | :---: |
| `[Screenshot 1]` | `[Screenshot 2]` |
| **Copilot Chat** | **System Architecture** |
| `[Screenshot 3]` | `[Screenshot 4]` |

---

##  Features

- ✅ **Layout-aware PDF parsing**
- ✅ **Hybrid Retrieval** (Dense + Graph + Lexical)
- ✅ **Knowledge Graph Construction**
- ✅ **Multi-Agent Reasoning**
- ✅ **Streaming Responses**
- ✅ **Source Citations**
- ✅ **Industrial Knowledge Graph**
- ✅ **JWT Authentication**
- ✅ **Self-Healing Queue**
- ✅ **Production-grade Backend**

---

##  Built on AMD

Embedding, chunking, parsing, generation, retrieval - all AI-related components were offloaded to AMD GPU notebooks and were accessed through ngrok tunnels.

| Task | Technology |
|------|------------|
| **LLM Inference** | ROCm + vLLM |
| **OCR / Parsing** | IBM Docling |
| **Embeddings** | FastEmbed |
| **GPU Platform** | AMD AI Notebooks |
| **API Boundary** | OpenAI Compatible |

**Why this matters:**
- Zero code changes between OpenAI and AMD inference.
- Complete offloading of heavy ML components to dedicated AMD hardware.
- Ready for secure, on-premise enterprise deployments.

The AMD AI Notebook exposes unified AI endpoints via ngrok tunnels, which are consumed natively by the Cortex backend.

---

##  Architecture

```text
        Next.js (Frontend)
               ↓
      FastAPI (API Gateway)
               ↓
    RQ Workers (Async Queue)
               ↓
     Hybrid Retrieval Engine
               ↓
   Multi-Agent Reasoning (P3)
               ↓
 +--------------------------+
 |  Qdrant | Neo4j | Postgres |
 +--------------------------+
               ↓
    AMD ROCm + vLLM (Compute)
```

---

##  Data Flow Diagrams

### 1. File Upload to Graph Generation (Ingestion)

```mermaid
graph TD
    A[User / Frontend] -->|Uploads PDF| B(FastAPI Gateway)
    B -->|Saves to Disk| C[(File Storage)]
    B -->|Enqueues Job| D[Redis / RQ]
    D -->|Pops Job| E(Ingestion Worker)
    E -->|1. Parse Document| F[IBM Docling / AMD]
    F -->|Parsed Content| E
    E -->|2. Generate Embeddings| G[FastEmbed / AMD]
    G -->|Embeddings| E
    E -->|3. Extract Entities| H[vLLM / AMD]
    H -->|Graph Data| E
    E -->|Store Nodes/Edges| I[(Neo4j)]
    E -->|Store Embeddings| J[(Qdrant)]
    E -->|Update Metadata| K[(PostgreSQL)]
```

### 2. Query Retrieval Pipeline

```mermaid
graph TD
    A[User / Frontend] -->|Asks Question| B(FastAPI Gateway)
    B -->|Query| C(Multi-Agent System)
    C -->|Generate Embedding| D[FastEmbed / AMD]
    C -->|Vector Search| E[(Qdrant)]
    C -->|Graph Traversal| F[(Neo4j)]
    E -->|Vector Results| G(Hybrid Retrieval Engine)
    F -->|Graph Results| G
    G -->|RRF Fusion & Context| H[Combined Context]
    H -->|Prompt w/ Context| I[vLLM / AMD]
    I -->|Streaming Response| C
    C -->|Streams Answer & Citations| A
```

---

##  Demo Flow

**Upload PDF** ➔ **Graph Builds** ➔ **Ask Question** ➔ **Get Cited Answer** ➔ **Explore Graph**

---

## 🛠️ Tech Stack

| Layer      | Tech            |
| ---------- | --------------- |
| **Frontend**   | Next.js 16      |
| **Backend**    | FastAPI         |
| **Vector DB**  | Qdrant          |
| **Graph DB**   | Neo4j           |
| **Metadata**   | PostgreSQL      |
| **Queue**      | Redis + RQ      |
| **AI Compute** | AMD ROCm + vLLM |
| **OCR**        | IBM Docling     |
| **Embeddings** | FastEmbed       |

---

##  Repository Structure

Judges, start here to navigate the codebase:

```text
cortex/
├── backend/
│   ├── ingestion_worker/  # P1: Parsing, embedding, and KG extraction
│   ├── app/retrieval/     # P2: Hybrid Retrieval (Dense, Lexical, Graph)
│   ├── app/agents/        # P3: LangGraph Multi-Agent System
│   └── fabric_api/        # FastAPI Application Layer
├── frontend/              # Next.js User Interface
├── scripts/               # Deployment and utility scripts
├── notebooks/             # AMD AI Notebooks for vLLM deployment
├── docs/                  # Architecture & Design Specs
└── docker-compose.yml     # Local Infrastructure
```

###  Where to Look
-  **`backend/ingestion_worker`** → Knowledge Graph Construction
-  **`backend/app/retrieval`** → Hybrid Retrieval Engine & RRF Fusion
-  **`backend/app/agents`** → LangGraph Multi-Agent System

---

## 💻 Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- AMD AI Notebook

### 1. AMD Notebook Setup
Upload `cortex_unified_notebook.ipynb` to the AMD AI Notebooks platform. Run the cells to expose the unified ML gateway endpoints via Ngrok. 

### 2. Infrastructure (Docker)
```bash
docker compose up -d
```

### 3. Backend Setup
```bash
cd backend
cp .env.example .env
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
alembic upgrade head
uv run uvicorn backend.fabric_api.main:app --reload --port 8000
```

### 4. Ingestion Worker
*(In a separate terminal)*
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

---

##  Environment Variables

**Backend (`backend/.env`)**
| Variable | Description |
|----------|-------------|
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins for CORS |
| `DATABASE_URL` | PostgreSQL connection string |
| `DEBUG` | Enable debug mode (`true`/`false`) |
| `EMBEDDING_MODEL` | Embedding model name |
| `EMBEDDING_MODEL_ENDPOINT` | Embedding model API endpoint | (AMD AI Notebook tunneled via ngrok)
| `FAST_MODEL` | Lightweight LLM used for fast responses |
| `FAST_MODEL_API_KEY` | API key for the fast LLM |
| `FAST_MODEL_BASE_URL` | Base URL of the fast LLM provider | (AMD AI Notebook tunneled via ngrok)
| `LLM_API_KEY` | API key for the primary LLM |
| `LLM_BASE_URL` | Base URL of the primary LLM provider | (AMD AI Notebook tunneled via ngrok)
| `LLM_MODEL` | Primary LLM model name | 
| `NEO4J_PASSWORD` | Neo4j database password |
| `NEO4J_URI` | Graph database connection URI |
| `NEO4J_USER` | Neo4j database username |
| `PROJECT_NAME` | Application name |
| `QDRANT_API_KEY` | Qdrant Cloud API key (optional for local instances) |
| `QDRANT_COLLECTION` | Qdrant collection name |
| `QDRANT_URL` | Qdrant server URL |
| `REDIS_URL` | Redis connection URL |
| `REMOTE_PARSER_URL` | Remote Docling parser endpoint | (AMD AI Notebook tunneled via ngrok)
| `S3_ACCESS_KEY_ID` | S3-compatible storage access key |
| `S3_BUCKET_NAME` | S3 bucket name |
| `S3_ENDPOINT_URL` | S3-compatible storage endpoint |
| `S3_REGION` | S3 bucket region |
| `S3_SECRET_ACCESS_KEY` | S3-compatible storage secret key |

**Frontend (`frontend/.env`)**
| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Base URL of the backend API |
| `NEXT_PUBLIC_API_PREFIX` | Versioned API path prefix |
| `NEXT_PUBLIC_APP_NAME` | Application name displayed in the UI |
| `NEXT_PUBLIC_DEFAULT_ENTITY` | Default entity shown in the knowledge graph |
| `NEXT_PUBLIC_DEFAULT_GRAPH_DEPTH` | Default graph traversal depth (number of hops) |
| `NEXT_PUBLIC_MAX_UPLOAD_MB` | Maximum file upload size (MB) |
| `NEXT_PUBLIC_REQUEST_TIMEOUT_MS` | Timeout for non-streaming API requests (ms) |

---

##  Production Deployment

| Service | Hosted On |
|---------|-----------|
| **Frontend** | Vercel |
| **Backend API** | Render |
| **ML Gateway (Inclunding parsing and embedding)** | AMD AI Notebooks |
| **Vector DB** | Qdrant Cloud |
| **Graph DB** | Neo4j AuraDB |
| **Relational DB** | Neon Postgres |
| **Cache** | Redis |
| **Object Storage** | Supabase S3-Compatible Storage |

---

##  Roadmap

- [ ] Kafka Integration for high-throughput ingestion
- [ ] Comprehensive Observability (Prometheus + OpenTelemetry)
- [ ] Fine-grained Server-side RBAC
- [ ] P&ID Vision (Piping and Instrumentation Diagrams)
- [ ] Industrial Vision-Language Models (VLM)
- [ ] Advanced Graph Analytics
