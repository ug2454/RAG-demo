#!/usr/bin/env python3
"""
Detailed ChromaDB inspection script with SQL/NoSQL comparison and vector visualization.
This helps you understand how vector databases store and retrieve data.
"""

import chromadb
import json

# Connect to ChromaDB
client = chromadb.HttpClient(host="localhost", port=8003)
collection = client.get_or_create_collection("documents")

print("=" * 100)
print("🔍 DETAILED CHROMADB INSPECTION - Understanding Vector Databases")
print("=" * 100)

# Get all data
data = collection.get(include=["documents", "metadatas", "embeddings"])

print(f"\n📊 DATABASE OVERVIEW")
print("-" * 100)
print(f"Total Records (Chunks): {len(data['ids'])}")
print(f"Collection Name: 'documents'")

if len(data['ids']) == 0:
    print("\n⚠️  No documents found. Upload a document first!")
    exit()

# Show embedding dimensions
if 'embeddings' in data and len(data['embeddings']) > 0:
    embedding_dim = len(data['embeddings'][0])
    print(f"Embedding Dimensions: {embedding_dim} (each chunk is a {embedding_dim}-dimensional vector)")
    print(f"Embedding Model: text-embedding-ada-002 (OpenAI)")

print("\n" + "=" * 100)
print("📚 SQL vs NoSQL vs VECTOR DATABASE - Comparison")
print("=" * 100)
print("""
┌─────────────────┬──────────────────┬──────────────────┬─────────────────────┐
│   Concept       │   SQL Database   │   NoSQL (JSON)   │   Vector Database   │
├─────────────────┼──────────────────┼──────────────────┼─────────────────────┤
│ Storage Format  │ Tables (Rows/    │ Documents (JSON)  │ Vectors + Metadata  │
│                 │ Columns)          │                  │                     │
├─────────────────┼──────────────────┼──────────────────┼─────────────────────┤
│ Primary Key     │ ID (integer)      │ _id (string)      │ ID (string)         │
├─────────────────┼──────────────────┼──────────────────┼─────────────────────┤
│ Data Structure  │ Structured rows  │ Flexible JSON     │ Vector (array) +    │
│                 │                  │                   │ Text + Metadata     │
├─────────────────┼──────────────────┼──────────────────┼─────────────────────┤
│ Search Method   │ Exact match      │ Field queries     │ Semantic similarity │
│                 │ (WHERE clause)   │ (MongoDB query)   │ (cosine distance)   │
├─────────────────┼──────────────────┼──────────────────┼─────────────────────┤
│ Query Example   │ SELECT * FROM    │ db.find({name:    │ collection.query(   │
│                 │ users WHERE      │ "John"})          │ query_embeddings=   │
│                 │ name = 'John'   │                   │ [vector])           │
└─────────────────┴──────────────────┴──────────────────┴─────────────────────┘
""")

print("\n" + "=" * 100)
print("🗂️  HOW YOUR DATA IS STORED IN CHROMADB")
print("=" * 100)

# Group by document
from collections import defaultdict
by_doc = defaultdict(lambda: {"chunks": [], "filename": None, "doc_id": None})

for i, (doc_id, doc_text, meta) in enumerate(zip(data['ids'], data['documents'], data['metadatas'])):
    filename = meta.get('filename', 'Unknown')
    doc_uuid = meta.get('doc_id', 'Unknown')
    chunk_idx = meta.get('chunk_id', i)
    
    by_doc[doc_uuid]['chunks'].append({
        'id': doc_id,
        'text': doc_text,
        'chunk_index': chunk_idx,
        'metadata': meta
    })
    by_doc[doc_uuid]['filename'] = filename
    by_doc[doc_uuid]['doc_id'] = doc_uuid

print(f"\n📁 You have {len(by_doc)} document(s) stored:\n")

for doc_uuid, doc_info in by_doc.items():
    filename = doc_info['filename']
    chunks = doc_info['chunks']
    print(f"📄 Document: {filename}")
    print(f"   Document UUID: {doc_uuid}")
    print(f"   Total Chunks: {len(chunks)}")
    print(f"   ")
    print(f"   Chunk Structure (like rows in SQL, but with vectors):")
    print(f"   ┌─────────────────────────────────────────────────────────────────────────┐")
    print(f"   │ ID (Primary Key)  │ Text Content      │ Embedding Vector │ Metadata   │")
    print(f"   ├─────────────────────────────────────────────────────────────────────────┤")
    
    for chunk in chunks[:3]:  # Show first 3 chunks
        chunk_id = chunk['id']
        text_preview = chunk['text'][:40].replace('\n', ' ') + "..." if len(chunk['text']) > 40 else chunk['text']
        print(f"   │ {chunk_id[:20]}... │ {text_preview[:30]:<30} │ [1536 dims]     │ {json.dumps(chunk['metadata'])[:30]}... │")
    
    if len(chunks) > 3:
        print(f"   │ ... ({len(chunks)-3} more chunks) ...                                                      │")
    print(f"   └─────────────────────────────────────────────────────────────────────────┘")
    print()

print("\n" + "=" * 100)
print("🔢 UNDERSTANDING EMBEDDINGS (VECTORS)")
print("=" * 100)
print("""
Each chunk of text is converted into a VECTOR (array of numbers) using OpenAI's embedding model.

Example:
  Text: "I have 5 years of experience in QA automation"
  
  Embedding Vector (first 10 numbers shown):
  [0.0123, -0.0456, 0.0789, ..., 0.0234]  (1536 total numbers)
  
  This vector represents the SEMANTIC MEANING of the text.
  Similar texts have similar vectors (close in high-dimensional space).
""")

if 'embeddings' in data and len(data['embeddings']) > 0:
    sample_embedding = data['embeddings'][0]
    print(f"\n📊 Sample Embedding from First Chunk:")
    print(f"   Dimensions: {len(sample_embedding)}")
    print(f"   First 10 values: {sample_embedding[:10]}")
    print(f"   Min value: {min(sample_embedding):.6f}")
    print(f"   Max value: {max(sample_embedding):.6f}")
    print(f"   Average: {sum(sample_embedding)/len(sample_embedding):.6f}")

print("\n" + "=" * 100)
print("🔍 HOW SEMANTIC SEARCH WORKS")
print("=" * 100)
print("""
When you ask: "What are my skills?"

1. Your question is converted to an embedding vector
2. ChromaDB calculates COSINE SIMILARITY between your question vector 
   and all stored chunk vectors
3. Returns the TOP 5 most similar chunks (not exact matches, but 
   semantically related!)
4. These chunks are sent to the LLM to generate an answer

This is DIFFERENT from SQL:
  - SQL: WHERE skill = "Java" (exact match)
  - Vector DB: Finds chunks about "programming", "coding", "software" 
    even if they don't contain the word "Java"
""")

# Demonstrate a query
print("\n" + "=" * 100)
print("🧪 DEMONSTRATION: Semantic Search Query")
print("=" * 100)

test_query = "What are my technical skills?"
print(f"\nQuery: '{test_query}'")
print("\nPerforming semantic search...")

try:
    results = collection.query(
        query_texts=[test_query],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n✅ Found {len(results['ids'][0])} most relevant chunks:\n")
    
    for i, (chunk_id, doc, meta, distance) in enumerate(zip(
        results['ids'][0], 
        results['documents'][0], 
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"Rank {i} (Similarity Score: {1-distance:.4f} - higher is better):")
        print(f"  📄 From: {meta.get('filename', 'Unknown')}")
        print(f"  📝 Text: {doc[:200]}...")
        print(f"  🔗 Chunk ID: {chunk_id}")
        print()
except Exception as e:
    print(f"⚠️  Could not perform query: {e}")

print("\n" + "=" * 100)
print("💾 PHYSICAL STORAGE")
print("=" * 100)
print("""
ChromaDB stores data in:
  - chroma.sqlite3: SQLite database (metadata, IDs, relationships)
  - Binary files (*.bin): Vector embeddings (optimized for fast similarity search)
  
This is a HYBRID approach:
  - SQLite for structured metadata (like SQL)
  - Binary files for vector data (optimized for vector operations)
""")

print("\n" + "=" * 100)
print("✅ SUMMARY")
print("=" * 100)
print(f"""
Your RAG system stores:
  ✅ {len(data['ids'])} text chunks
  ✅ Each chunk has a {embedding_dim if 'embeddings' in data and len(data['embeddings']) > 0 else 'N/A'}-dimensional embedding vector
  ✅ Metadata (filename, document ID, chunk index) stored like JSON
  ✅ Fast semantic search using cosine similarity

Think of it as:
  - SQL table: Each row = one chunk
  - Vector column: The embedding (1536 numbers)
  - Text column: The actual chunk text
  - Metadata column: JSON with filename, doc_id, etc.
  - Search: Instead of WHERE clause, uses vector similarity!
""")

print("=" * 100)

