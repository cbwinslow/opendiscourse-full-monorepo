import { useState } from "react";

const mockEntities = [
  { id: 1, name: "Jane Doe", type: "Politician" },
  { id: 2, name: "Committee on Finance", type: "Committee" },
  { id: 3, name: "John Smith", type: "Official" },
];

export default function Entities() {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-gray-900 text-white p-4">
        <h2 className="font-bold text-lg mb-4">Entities</h2>
        <ul>
          {mockEntities.map((e) => (
            <li
              key={e.id}
              className={`mb-2 p-2 rounded cursor-pointer hover:bg-gray-700 ${selected === e.id ? "bg-gray-700" : ""}`}
              onClick={() => setSelected(e.id)}
            >
              {e.name} <span className="text-xs text-gray-400">({e.type})</span>
            </li>
          ))}
        </ul>
      </aside>
      <main className="flex-1 p-8">
        {!selected ? (
          <div className="text-gray-500">Select an entity to view details.</div>
        ) : (
          <div className="bg-white rounded shadow p-6">
            <h2 className="text-2xl font-bold mb-2">{mockEntities.find(e => e.id === selected)?.name}</h2>
            <p className="text-blue-800 mb-2">Type: {mockEntities.find(e => e.id === selected)?.type}</p>
            <p className="text-gray-700">Details and declarations will appear here.</p>
          </div>
        )}
      </main>
    </div>
  );
}
