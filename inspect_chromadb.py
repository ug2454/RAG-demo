#!/usr/bin/env python3
"""
Simple script to inspect ChromaDB data stored in your RAG application.
Run this from your project root directory.
"""

import chromadb

# Connect to your ChromaDB server (make sure it's running!)
client = chromadb.HttpClient(host="localhost", port=8003)
collection = client.get_or_create_collection("documents")

print("=" * 80)
print("CHROMADB INSPECTION REPORT")
print("=" * 80)

# Get all data from the collection
data = collection.get()

print(f"\n📊 Total Records: {len(data['ids'])}")
print(f"📁 Collection Name: 'documents'")

if len(data['ids']) == 0:
    print("\n⚠️  No documents found in ChromaDB. Upload a document first!")
else:
    print(f"\n📝 Document IDs (first 10):")
    for i, doc_id in enumerate(data['ids'][:10], 1):
        print(f"   {i}. {doc_id}")
    
    if len(data['ids']) > 10:
        print(f"   ... and {len(data['ids']) - 10} more")
    
    print(f"\n📄 Sample Documents (first 3 chunks):")
    print("-" * 80)
    for i in range(min(3, len(data['documents']))):
        doc = data['documents'][i]
        meta = data['metadatas'][i]
        doc_id = data['ids'][i]
        
        print(f"\n🔹 Chunk ID: {doc_id}")
        print(f"   Filename: {meta.get('filename', 'N/A')}")
        print(f"   Document ID: {meta.get('doc_id', 'N/A')}")
        print(f"   Chunk Index: {meta.get('chunk_id', 'N/A')}")
        print(f"   Text Preview: {doc[:200]}..." if len(doc) > 200 else f"   Text: {doc}")
        print("-" * 80)
    
    # Group by document (filename)
    print(f"\n📚 Documents by Filename:")
    from collections import defaultdict
    by_filename = defaultdict(list)
    for i, meta in enumerate(data['metadatas']):
        filename = meta.get('filename', 'Unknown')
        by_filename[filename].append(i)
    
    for filename, indices in by_filename.items():
        print(f"   📄 {filename}: {len(indices)} chunks")
        print(f"      Chunk IDs: {', '.join([data['ids'][idx] for idx in indices[:5]])}")
        if len(indices) > 5:
            print(f"      ... and {len(indices) - 5} more chunks")

print("\n" + "=" * 80)
print("✅ Inspection complete!")
print("=" * 80)

