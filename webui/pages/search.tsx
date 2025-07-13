import { useState } from "react";

interface Answer {
  answer: string;
  sources?: { content: string; source: string }[];
}

export default function SearchPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<Answer | null>(null);
  const [loading, setLoading] = useState(false);
  const ask = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Query failed");
      setResult(data);
    } catch (e: any) {
      setResult({ answer: `Error: ${e.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "2rem auto", padding: 24 }}>
      <h1>Ask a Question</h1>
      <form onSubmit={ask} style={{ marginTop: 16 }}>
        <input
          style={{ width: "70%" }}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" style={{ marginLeft: 8 }}>Ask</button>
      </form>
      {loading && <p>Loading...</p>}
      {result && (
        <div style={{ marginTop: 16 }}>
          <h2>Answer</h2>
          <p>{result.answer}</p>
          {result.sources && (
            <>
              <h3>Sources</h3>
              <ul>
                {result.sources.map((s, i) => (
                  <li key={i}>
                    <strong>{s.source}:</strong> {s.content}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
