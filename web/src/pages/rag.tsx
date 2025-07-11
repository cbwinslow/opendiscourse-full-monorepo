import React from "react";

export default function RAGReports() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-4 text-blue-900">RAG Reports</h1>
      <p className="mb-6 text-blue-800 max-w-2xl">
        Run retrieval-augmented generation (RAG) reports on ingested documents. Generate summaries, classifications, and fact-checks using the latest AI models.
      </p>
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-2">Available Reports</h2>
        <ul className="list-disc pl-6 text-blue-900">
          <li>Summary Report</li>
          <li>Classification Report</li>
          <li>Fact-Check Report</li>
        </ul>
        <button className="mt-6 px-4 py-2 bg-blue-700 text-white rounded hover:bg-blue-800 transition">
          Run Selected Report
        </button>
      </div>
    </div>
  );
}
