import React, { useState } from "react";

const mockResults = [
  { id: 1, name: "Jane Doe", type: "Politician", snippet: "Voted on Bill 123..." },
  { id: 2, name: "Committee on Finance", type: "Committee", snippet: "Held hearing on..." },
  { id: 3, name: "John Smith", type: "Official", snippet: "Issued statement..." },
];

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(mockResults);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // In real app, filter or fetch results here
    setResults(mockResults.filter(r => r.name.toLowerCase().includes(query.toLowerCase())));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-4 text-blue-900">Search</h1>
      <form onSubmit={handleSearch} className="mb-6 flex gap-2">
        <input
          className="px-4 py-2 border rounded w-80"
          placeholder="Search for people, committees, or documents..."
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <button className="px-4 py-2 bg-blue-700 text-white rounded hover:bg-blue-800 transition" type="submit">
          Search
        </button>
      </form>
      <div className="bg-white rounded shadow p-6">
        <h2 className="text-xl font-semibold mb-2">Results</h2>
        <ul>
          {results.length === 0 && <li className="text-gray-500">No results found.</li>}
          {results.map(r => (
            <li key={r.id} className="mb-4 border-b pb-2">
              <div className="font-bold text-blue-800">{r.name} <span className="text-xs text-gray-400">({r.type})</span></div>
              <div className="text-gray-700">{r.snippet}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
