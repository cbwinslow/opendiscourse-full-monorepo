import { Link } from 'next/link';

export default function Index() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-600">OpenDiscourse</span>
            </div>
            <div className="hidden md:flex space-x-8">
              <Link href="/search" className="text-gray-700 hover:text-blue-600">Search</Link>
              <Link href="/chat" className="text-gray-700 hover:text-blue-600">Chat</Link>
              <Link href="/admin" className="text-gray-700 hover:text-blue-600">Admin</Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to OpenDiscourse</h1>
        <p className="text-gray-600">
          A comprehensive platform for legal, political, and public discourse analysis.
        </p>
      </main>
    </div>
  );
}
