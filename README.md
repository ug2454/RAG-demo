# RAG Web App Demo: Retrieval-Augmented Generation

A full-stack web app to learn and experiment with Retrieval-Augmented Generation (RAG). Upload documents (PDF/TXT), ask questions, and see how relevant chunks are retrieved and used for LLM answers. Built for transparency and education.

---

## What is Retrieval-Augmented Generation (RAG)?
RAG is an LLM application architectural pattern where answers are generated *not just* from model knowledge, but also from *external relevant documents*, retrieved dynamically at inference time.

**RAG Pipeline:**
1. **Ingest** documents (parse + chunk).
2. **Embed** each chunk (e.g., OpenAI embeddings).
3. **Store** vectors in a semantic search database (ChromaDB).
4. **Retrieve** best-matching chunks at query time.
5. **Generate** answer using LLM, conditioned on both query and retrieved chunks for richer, up-to-date, transparent results.

```
      +------------+
      |  Upload    |
      | PDF / TXT  |
      +-----+------+
            |
   Parse, Chunk, Embed (OpenAI)
            |
      [ChromaDB Vector Store]
            |
      +-----v------+
      |   Search   | <--- User Query
      +-----+------+
            |  Retrieve Chunks
      +-----v------+   +-----------+
      |   LLM      +-->|   Answer  |
      +------------+   +-----------+
```

---

## Architecture
- **Frontend**: React (document upload, question UI, educational details).
- **Backend**: FastAPI (Python, chunking, embedding, storage, and retrieval).
- **Vector DB**: ChromaDB (stores and searches semantic vectors).
- **Embeddings & Generation**: OpenAI API (`text-embedding-ada-002`, GPT).

---

## Setup & Usage
### 1. Prerequisites
- Docker & Docker Compose
- OpenAI API Key

### 2. Quickstart (Recommended: Docker Compose)
```
# Clone repo, enter directory and set OpenAI key
export OPENAI_API_KEY=sk-...
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend:  http://localhost:8000/docs (FastAPI UI)

### 3. Manual Dev Setup (if not using Docker)
- Backend: Create Python venv, install dependencies from `backend/requirements.txt`, then:
  ```
  export OPENAI_API_KEY=sk-...
  uvicorn main:app --reload
  ```
- Frontend: `cd frontend && npm install && npm start`

---

## Key API Endpoints
- `POST /upload/` — Upload PDF/TXT (multipart), returns chunk + metadata
- `POST /ask/` — Ask a question (form field `query`), returns `answer`, `evidence`, and (in educational mode) raw context

---

## Example Workflow
1. Upload a PDF (or TXT). See how text is chunked and embedded.
2. Ask a question. App will (soon) retrieve matching chunks, show the full retrieval context, and pass context + question to LLM.
3. Toggle **Educational Mode** in UI to see what the LLM "sees."

---

## Educational Mode
- Toggle to show raw chunks (retrieval context for LLM)
- Helps build intuition about why the LLM answers as it does

---

## Customization & Extending
- Swap ChromaDB for another vector DB
- Use alternative embedding models
- Customize chunk sizes/overlap

---
## Credits & Libraries
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [ChromaDB](https://www.trychroma.com/)
- [OpenAI Python](https://github.com/openai/openai-python)
- [PyPDF2](https://pypdf2.readthedocs.io/en/3.0.0/)
- Created by Uday Garg
- [LinkedIn](https://www.linkedin.com/in/uday-garg-45b611280/)
