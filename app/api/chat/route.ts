import { streamText } from "ai"

/**
 * POST /api/chat
 *
 * This route handler proxies requests to the Vercel AI Gateway.
 * It receives messages from the frontend and streams the AI response back.
 */
export async function POST(req: Request) {
  try {
    const { messages, model } = await req.json()

    if (!messages || !Array.isArray(messages)) {
      return new Response(JSON.stringify({ error: "Invalid request: messages array required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      })
    }

    const selectedModel = model || "google/gemini-2.0-flash-001"

    const lastIndex = messages.length - 1
    const transformedMessages = messages.map(
      (m: { role: string; content: string; imageData?: string }, index: number) => {
        // Only process image for the last user message
        const isLastUserMessage = index === lastIndex && m.role === "user"

        if (isLastUserMessage && m.imageData && m.imageData.startsWith("data:image/")) {
          // For the current message with an image, use multimodal content format
          return {
            role: m.role as "user" | "assistant",
            content: [
              {
                type: "image" as const,
                image: m.imageData,
              },
              {
                type: "text" as const,
                text: m.content || "Describe this image in detail.",
              },
            ],
          }
        }

        // For all other messages (history), use text only
        // If there was an image, mention it in the text
        let textContent = m.content
        if (m.imageData && !isLastUserMessage) {
          textContent = m.content || "[User shared an image]"
        }

        return {
          role: m.role as "user" | "assistant",
          content: textContent,
        }
      },
    )

    // Filter out any messages with empty content
    const validMessages = transformedMessages.filter((m: { content: string | object[] }) => {
      if (typeof m.content === "string") {
        return m.content.trim().length > 0
      }
      return true // Keep multimodal messages
    })

    if (validMessages.length === 0) {
      return new Response(JSON.stringify({ error: "No valid messages to process" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      })
    }

    const result = streamText({
      model: selectedModel,
      messages: validMessages,
      system: `You are a helpful, friendly AI assistant. You provide clear, concise, and accurate responses. 
When explaining code or technical concepts, use markdown formatting with code blocks where appropriate.
Be conversational but professional. If you're unsure about something, say so honestly.
When analyzing images, describe them in detail and answer any questions about them.`,
    })

    return result.toTextStreamResponse()
  } catch (error) {
    console.error("Chat API error:", error)

    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "An unexpected error occurred",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    )
  }
}
