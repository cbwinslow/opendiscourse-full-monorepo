import { useState } from "react";

// Dummy data for demonstration
const entities = [
  { id: 1, name: "Jane Doe", type: "Politician" },
  { id: 2, name: "Committee on Finance", type: "Committee" },
  { id: 3, name: "John Smith", type: "Official" },
];

const entityDetails = {
  1: { bio: "Jane Doe is a senator from...", declarations: ["Declaration 1", "Declaration 2"] },
  2: { bio: "The Committee on Finance oversees...", declarations: ["Hearing 2024-01", "Report 2024-02"] },
  3: { bio: "John Smith is a government official...", declarations: ["Statement 2023-11"] },
};

export default function Workspace() {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-4 font-bold text-xl border-b border-gray-700">Search</div>
        <input
          className="m-4 px-3 py-2 rounded bg-gray-800 text-white"
          placeholder="Search people or entities..."
        />
        <nav className="flex-1 overflow-y-auto">
          {entities.map((e) => (
            <div
              key={e.id}
              className={`px-4 py-2 cursor-pointer hover:bg-gray-700 ${selected === e.id ? "bg-gray-700" : ""}`}
              onClick={() => setSelected(e.id)}
            >
              <span className="font-semibold">{e.name}</span>
              <span className="ml-2 text-xs text-gray-400">{e.type}</span>
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Pane */}
      <main className="flex-1 flex flex-col">
        <div className="bg-white border-b px-6 py-4 font-bold text-lg shadow">
          {selected ? entities.find(e => e.id === selected)?.name : "Welcome to Open Discourse Workspace"}
        </div>
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          {!selected ? (
            <div className="text-gray-400 text-xl">Select an entity to view details</div>
          ) : (
            <div className="text-gray-800 text-lg">
              <div className="font-bold mb-2">{entities.find(e => e.id === selected)?.type}</div>
              <div className="mb-4">{entityDetails[selected]?.bio}</div>
              <div>
                <span className="font-semibold">Declarations:</span>
                <ul className="list-disc pl-6">
                  {entityDetails[selected]?.declarations.map((d, i) => (
                    <li key={i}>{d}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Details Pane */}
      {selected && (
        <aside className="w-96 bg-white border-l flex flex-col">
          <div className="p-4 border-b font-bold text-blue-900">Entity Details</div>
          <div className="p-4">
            <div className="font-semibold mb-2">{entities.find(e => e.id === selected)?.name}</div>
            <div className="mb-2 text-gray-700">{entityDetails[selected]?.bio}</div>
            <div>
              <span className="font-semibold">Declarations:</span>
              <ul className="list-disc pl-6 text-gray-800">
                {entityDetails[selected]?.declarations.map((d, i) => (
                  <li key={i}>{d}</li>
                ))}
              </ul>
            </div>
          </div>
        </aside>
      )}
    </div>
  );
}
