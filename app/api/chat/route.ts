import { openai } from "@ai-sdk/openai"
import { streamText } from "ai"

export async function POST(req: Request) {
  const apiKey = process.env.OPENAI_API_KEY
  console.log("[chat] API key present:", !!apiKey, "length:", apiKey?.length)

  try {
    const { messages } = await req.json()

    if (!messages || !Array.isArray(messages)) {
      return new Response(JSON.stringify({ error: "messages array required" }), { status: 400 })
    }

    const validMessages = messages
      .map((m: { role: string; content: string }) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      }))
      .filter((m: { content: string }) => m.content.trim().length > 0)

    if (validMessages.length === 0) {
      return new Response(JSON.stringify({ error: "No valid messages" }), { status: 400 })
    }

    console.log("[chat] Calling OpenAI gpt-4.1-mini with", validMessages.length, "messages")

    const result = await streamText({
      model: openai("gpt-4.1-mini"),
      messages: validMessages,
      system: "You are a helpful, friendly AI assistant. Be conversational but professional.",
    })

    console.log("[chat] Stream created, returning response")
    return result.toTextStreamResponse()
  } catch (error) {
    console.error("[chat] ERROR:", error)
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500 }
    )
  }
}
