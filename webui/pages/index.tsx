import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>OpenDiscourse Web UI</h1>
      <ul style={{ marginTop: "1rem" }}>
        <li>
          <Link href="/diagnostics">Diagnostics</Link>
        </li>
        <li>
          <Link href="/upload">Upload Document</Link>
        </li>
        <li>
          <Link href="/search">Search</Link>
        </li>
      </ul>
    </main>
  );
}
