import React from "react";

export default function Ingestion() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-4 text-blue-900">Document Ingestion</h1>
      <p className="mb-6 text-blue-800 max-w-2xl">
        Ingest government documents from sources like govinfo.gov and congress.gov. Track ingestion status, view logs, and trigger new ingestion jobs.
      </p>
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-2">Ingestion Status</h2>
        <ul className="list-disc pl-6 text-blue-900">
          <li>govinfo.gov: <span className="text-green-600">Up to date</span></li>
          <li>congress.gov: <span className="text-yellow-600">Syncing...</span></li>
        </ul>
        <button className="mt-6 px-4 py-2 bg-blue-700 text-white rounded hover:bg-blue-800 transition">
          Trigger Ingestion
        </button>
      </div>
    </div>
  );
}
