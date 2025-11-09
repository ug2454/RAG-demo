"""
RAG (Retrieval-Augmented Generation) Demo Backend

1. Users upload documents (PDF or TXT). Documents are parsed, chunked (for retrievable units),
   and each chunk is embedded using OpenAI's embedding API.
2. Embeddings and chunk text are stored in ChromaDB (vector database) for semantic search.
3. On question, query is embedded and the database searched for relevant chunks.
4. The retrieved chunks + question are sent to the LLM for synthesized answer generation (now fully implemented).

This file implements: Document upload and ingestion endpoints, chunking, embedding (OpenAI), storage in ChromaDB, retrieval, and LLM answer synthesis.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from utils.pdf_parser import extract_text_from_pdf, extract_text_from_txt, chunk_text
import chromadb
from chromadb.config import Settings
import uuid
import openai

# FastAPI backend recommended to run on port 8001 if ChromaDB server runs on 8000
# Start with: uvicorn main:app --host 0.0.0.0 --port 8001 --reload

app = FastAPI(title="RAG Educational Demo API", description="A demo backend for Retrieval-Augmented Generation (RAG) workflow.")

# Enable CORS for the frontend (adjust origins as appropriate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # Only allow the local React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- OpenAI API Key Setup ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# --- ChromaDB Setup ---
#   - Connect to standalone ChromaDB service running with 'chroma run --port 8002' or docker on port 8002
chroma_client = chromadb.HttpClient(host="localhost", port=8003)
collection = chroma_client.get_or_create_collection("documents")

# --- Embedding Utility ---
def embed_chunks_openai(chunks):
    """
    Given a list of text chunks, produces OpenAI embeddings for each chunk (batched requests).
    Returns a list of vector embeddings.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI API Key not set!")
    emb = []
    for i in range(0, len(chunks), 20):
        response = openai.embeddings.create(
            input=chunks[i:i+20],
            model="text-embedding-ada-002"
        )
        # Fixed for openai>=1.x: attribute access on Embedding objects
        sorted_embs = sorted(response.data, key=lambda x: x.index)
        emb.extend([d.embedding for d in sorted_embs])
    return emb

@app.post("/upload/")
def upload_document(file: UploadFile = File(...)):
    """
    Step 1: Document Upload/Ingestion for RAG
    -----------------------------------------
    Upload a PDF or TXT document. File is parsed and split into text chunks. Each chunk is embedded
    using OpenAI and all results are stored in a vector DB (Chroma).
    Returns chunk info for education and debugging.
    """
    filename = file.filename
    if not (filename.endswith('.pdf') or filename.endswith('.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key environment variable not set.")

    # --- 1. Parse content (PDF/TXT) ---
    try:
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file.file)
            filetype = 'pdf'
        else:
            text = extract_text_from_txt(file.file)
            filetype = 'txt'
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parsing failed: {str(e)}")

    # --- 2. Chunking ---
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text found to index.")
    doc_id = str(uuid.uuid4())

    # --- 3. Embeddings ---
    try:
        embeddings = embed_chunks_openai(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # --- 4. Store in ChromaDB ---
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"filename": filename, "doc_id": doc_id, "chunk_id": i} for i in range(len(chunks))]
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    preview = chunks[:3] if len(chunks) > 3 else chunks
    return {
        "filename": filename,
        "filetype": filetype,
        "num_chunks": len(chunks),
        "doc_id": doc_id,
        "chunk_preview": preview
    }

@app.post("/ask/")
def ask_question(query: str = Form(...)):
    """
    Step 2: Semantic Query & RAG Answer
    -----------------------------------
    1. Embed user question.
    2. Semantic search in ChromaDB for relevant chunks.
    3. Build LLM prompt from chunks + question.
    4. Call OpenAI chat completion for final answer.
    Returns the answer, evidence text, and LLM input context for educational mode.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key environment variable not set.")

    # --- 1. Embed the question ---
    try:
        query_emb = embed_chunks_openai([query])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # --- 2. Semantic search in ChromaDB ---
    try:
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=5,
            include=["documents", "metadatas"]
        )
        top_chunks = results["documents"][0]   # List of chunk texts
        evidence = top_chunks
        # Optionally use metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector DB query failed: {str(e)}")

    # --- 3. Build LLM context ---
    context = "\n---\n".join(top_chunks)
    prompt = (
        "You are an expert assistant. Given the following context chunks (from user files) and a question, "
        "give a concise answer based strictly on the context. Cite text by quoting or listing sources if helpful.\n\n"
        f"Context Chunks:\n{context}\n\nQuestion:\n{query}\n\nAnswer:"
    )

    # --- 4. Call OpenAI chat completion ---
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert RAG assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=400,
        )
        answer_text = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")

    return {
        "answer": answer_text,
        "evidence": evidence,
        "llm_context": prompt,
        "message": "Answer generated using retrieved context."
    }
