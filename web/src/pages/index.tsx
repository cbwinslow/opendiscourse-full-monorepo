import Link from "next/link";

const presidentialQuotes = [
	{
		quote: "Government of the people, by the people, for the people, shall not perish from the Earth.",
		author: "Abraham Lincoln",
	},
	{
		quote: "The best way to predict your future is to create it.",
		author: "Abraham Lincoln",
	},
	{
		quote: "Ask not what your country can do for you—ask what you can do for your country.",
		author: "John F. Kennedy",
	},
];

export default function Home() {
	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex flex-col">
			{/* Hero Section */}
			<header className="py-12 text-center">
				<h1 className="text-5xl font-extrabold text-blue-900 mb-4">Open Discourse</h1>
				<p className="text-xl text-blue-700 max-w-2xl mx-auto">
					Transparency, accountability, and insight into government documents and public declarations. Explore, search, and analyze with the power of open data.
				</p>
			</header>

			{/* Navigation Bar */}
			<nav className="flex justify-center gap-6 mt-8">
				<a href="/workspace" className="text-blue-700 hover:underline font-semibold">
					Workspace
				</a>
				<a href="/ingestion" className="text-blue-700 hover:underline font-semibold">
					Ingestion
				</a>
				<a href="/entities" className="text-blue-700 hover:underline font-semibold">
					Entities
				</a>
				<a href="/rag" className="text-blue-700 hover:underline font-semibold">
					RAG Reports
				</a>
				<a href="/search" className="text-blue-700 hover:underline font-semibold">
					Search
				</a>
				<a href="/about" className="text-blue-700 hover:underline font-semibold">
					About
				</a>
				<a href="/settings" className="text-blue-700 hover:underline font-semibold">
					Settings
				</a>
				<a href="/help" className="text-blue-700 hover:underline font-semibold">
					Help
				</a>
			</nav>

			{/* Hero Card */}
			<main className="flex-1 flex flex-col items-center justify-center">
				<Link href="/workspace" passHref>
					<div className="cursor-pointer bg-white shadow-xl rounded-2xl px-10 py-12 text-center transition-transform hover:scale-105 border-2 border-blue-200 max-w-xl">
						<h2 className="text-3xl font-bold text-blue-800 mb-2">Launch Open Discourse Workspace</h2>
						<p className="text-lg text-blue-600 mb-4">
							Dive into our interactive workspace to search, analyze, and report on public records.
						</p>
						<button className="mt-4 px-6 py-2 bg-blue-700 text-white rounded-lg font-semibold shadow hover:bg-blue-800 transition">
							Enter Workspace
						</button>
					</div>
				</Link>
			</main>

			{/* Quotes Section */}
			<section className="mt-16 mb-8">
				<h3 className="text-center text-2xl font-semibold text-blue-800 mb-6">Presidential Wisdom</h3>
				<div className="flex flex-wrap justify-center gap-8">
					{presidentialQuotes.map((q, i) => (
						<blockquote key={i} className="bg-blue-100 rounded-lg p-6 max-w-md shadow">
							<p className="italic text-blue-900 mb-2">"{q.quote}"</p>
							<footer className="text-right text-blue-700 font-medium">— {q.author}</footer>
						</blockquote>
					))}
				</div>
			</section>

			{/* What We Do */}
			<section className="bg-blue-50 py-12">
				<div className="max-w-4xl mx-auto px-4">
					<h2 className="text-2xl font-bold text-blue-900 mb-4">What is Open Discourse?</h2>
					<ul className="list-disc pl-6 text-blue-800 space-y-2">
						<li>Search and analyze government documents, committee records, and public declarations.</li>
						<li>Track politicians, organizations, and legislative actions in real time.</li>
						<li>Run custom reports and fact-checks in an interactive workspace inspired by modern developer tools.</li>
						<li>Empower citizens, journalists, and researchers with open, accessible data.</li>
					</ul>
				</div>
			</section>

			{/* Global Styles */}
			<style jsx global>{`
				body {
					font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
					background: linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%);
					color: #1e293b;
				}
				a {
					transition: color 0.2s;
				}
				a:hover {
					color: #2563eb;
				}
			`}</style>
		</div>
	);
}
