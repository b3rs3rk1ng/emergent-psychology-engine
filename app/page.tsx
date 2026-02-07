import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center gap-6">
      <h1 className="text-2xl font-semibold">Emergent Psychology Engine</h1>
      <p className="text-muted-foreground">Select a demo:</p>
      <div className="flex gap-4">
        <Link
          href="/orb"
          className="px-6 py-3 rounded-lg bg-black text-white hover:bg-gray-800 transition-colors"
        >
          Orb Shader
        </Link>
        <Link
          href="/chat"
          className="px-6 py-3 rounded-lg bg-black text-white hover:bg-gray-800 transition-colors"
        >
          AI Chat
        </Link>
      </div>
    </div>
  )
}
