import React, { useState } from "react";
import "./App.css";

function App() {
  // State for document upload
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [file, setFile] = useState(null);

  // State for query
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loadingAnswer, setLoadingAnswer] = useState(false);

  // Educational mode state
  const [eduMode, setEduMode] = useState(false);

  // Upload handler
  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setUploadResult(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const resp = await fetch("http://localhost:4444/upload/", {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      setUploadResult(data);
    } catch (err) {
      setUploadResult({ error: "Upload failed" });
    } finally {
      setUploading(false);
    }
  }

  // Question handler
  async function handleAsk(e) {
    e.preventDefault();
    if (!question) return;
    setLoadingAnswer(true);
    setAnswer(null);
    const formData = new FormData();
    formData.append("query", question);
    try {
      const resp = await fetch("http://localhost:4444/ask/", {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      setAnswer(data);
    } catch (err) {
      setAnswer({ error: "Query failed" });
    } finally {
      setLoadingAnswer(false);
    }
  }

  return (
    <div className="App" style={{ maxWidth: 650, margin: "40px auto", padding: 16 }}>
      <h1>RAG Demo — Retrieval Augmented Generation</h1>

      <div style={{ marginBottom: 14 }}>
        <input type="checkbox" id="eduToggle" checked={eduMode} onChange={e => setEduMode(e.target.checked)} />
        <label htmlFor="eduToggle" style={{ marginLeft: 8, fontWeight: 500 }}>
          Show Educational Details (chunks/context sent to LLM)
        </label>
      </div>

      <section style={{ marginBottom: 32, padding: 20, border: "1px solid #ddd", borderRadius: 8 }}>
        <h2>1. Upload Document (PDF or TXT)</h2>
        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept=".pdf,.txt"
            required
            onChange={e => setFile(e.target.files[0])}
            disabled={uploading}
          />
          <button type="submit" disabled={uploading || !file} style={{ marginLeft: 8 }}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>
        {uploadResult && (
          <div style={{ marginTop: 16 }}>
            {uploadResult.error ? (
              <span style={{ color: 'red' }}>{uploadResult.error}</span>
            ) : (
              <>
                <b>File:</b> {uploadResult.filename} <br />
                <b>Type:</b> {uploadResult.filetype} <br />
                <b>Chunks:</b> {uploadResult.num_chunks}<br />
                <b>Chunk Preview:</b>
                <pre style={{ background: '#f9f9f9', padding: 10, borderRadius: 6 }}>
                  {JSON.stringify(uploadResult.chunk_preview, null, 2)}
                </pre>
              </>
            )}
          </div>
        )}
      </section>

      <section style={{ marginBottom: 32, padding: 20, border: "1px solid #ddd", borderRadius: 8 }}>
        <h2>2. Ask a Question</h2>
        <form onSubmit={handleAsk}>
          <input
            type="text"
            style={{ width: "65%", marginRight: 8 }}
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="What do you want to know?"
            disabled={loadingAnswer}
            required
          />
          <button type="submit" disabled={loadingAnswer || !question}>
            {loadingAnswer ? "Asking..." : "Ask"}
          </button>
        </form>
        {answer && (
          <div style={{ marginTop: 16 }}>
            {answer.error ? (
              <span style={{ color: 'red' }}>{answer.error}</span>
            ) : (
              <>
                <b>Answer:</b> {answer.answer !== null ? answer.answer : <span style={{color:'gray'}}>Not implemented yet</span>} <br />
                <b>Evidence Chunks:</b>
                <pre style={{ background: '#f9f9f9', padding: 10, borderRadius: 6 }}>
                  {JSON.stringify(answer.evidence, null, 2)}
                </pre>
                <i>{answer.message}</i>
                {eduMode && (
                  <div style={{ margin: '12px 0', background: '#eef6fa', padding: 12, borderRadius: 6 }}>
                    <b>Educational Context:</b>
                    <pre style={{ background: '#f7fafc', padding: 8 }}>
                      {answer.llm_context ? answer.llm_context : "Details shown here when retrieval & answer are implemented."}
                    </pre>
                    {!answer.llm_context && <span style={{ color: '#aaa' }}>(RAG context preview not yet available.)</span>}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </section>
      <footer style={{ marginTop: 32, fontSize: 14, color: '#888' }}>
        <div>Built for learning and demonstration purposes.</div>
      </footer>
    </div>
  );
}

export default App;
