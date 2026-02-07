"use client"

import { useState, useEffect, useCallback } from "react"
import { MessageSquareDashed } from "lucide-react"
import { MessageList } from "./message-list"
import { Composer, type AIModel } from "./composer"
import { Button } from "@/components/ui/button"

// Data model for messages
export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  createdAt: Date
  imageData?: string
}

// localStorage key for persisting messages
const STORAGE_KEY = "chat-messages"
const MODEL_STORAGE_KEY = "chat-selected-model"

// Generates a unique ID for messages
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
}

export function ChatShell() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [selectedModel, setSelectedModel] = useState<AIModel>("google/gemini-2.0-flash-001")
  const [isLoaded, setIsLoaded] = useState(false)

  // Load messages from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        const messagesWithDates = parsed.map((msg: Message) => ({
          ...msg,
          createdAt: new Date(msg.createdAt),
        }))
        setMessages(messagesWithDates)
      }
      const savedModel = localStorage.getItem(MODEL_STORAGE_KEY) as AIModel | null
      if (savedModel) {
        setSelectedModel(savedModel)
      }
    } catch (e) {
      console.error("Failed to load from localStorage:", e)
    } finally {
      setIsLoaded(true)
    }
  }, [])

  // Persist messages to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
    } catch (e) {
      console.error("Failed to save messages to localStorage:", e)
    }
  }, [messages])

  const handleModelChange = useCallback((model: AIModel) => {
    setSelectedModel(model)
    localStorage.setItem(MODEL_STORAGE_KEY, model)
  }, [])

  // Send a message to the AI
  const sendMessage = useCallback(
    async (content: string, imageData?: string) => {
      if ((!content.trim() && !imageData) || isStreaming) return

      setError(null)

      const userMessage: Message = {
        id: generateId(),
        role: "user",
        content: content.trim() || "Describe this image",
        createdAt: new Date(),
        imageData,
      }

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: "",
        createdAt: new Date(),
      }

      const newMessages = [...messages, userMessage, assistantMessage]
      setMessages(newMessages)
      setIsStreaming(true)

      const controller = new AbortController()
      setAbortController(controller)

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: [...messages, userMessage].map((m) => ({
              role: m.role,
              content: m.content,
              imageData: m.imageData,
            })),
            model: selectedModel,
          }),
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
          throw new Error("No response body")
        }

        let accumulatedContent = ""

        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          accumulatedContent += chunk

          setMessages((prev) =>
            prev.map((msg) => (msg.id === assistantMessage.id ? { ...msg, content: accumulatedContent } : msg)),
          )
        }
      } catch (e) {
        if (e instanceof Error && e.name === "AbortError") {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessage.id ? { ...msg, content: msg.content || "[Cancelled]" } : msg,
            ),
          )
        } else {
          console.error("Error sending message:", e)
          setError(e instanceof Error ? e.message : "An error occurred")
          setMessages((prev) => prev.filter((msg) => msg.id !== assistantMessage.id))
        }
      } finally {
        setIsStreaming(false)
        setAbortController(null)
      }
    },
    [messages, isStreaming, selectedModel],
  )

  const retry = useCallback(() => {
    if (messages.length === 0) return
    const lastUserMessage = [...messages].reverse().find((m) => m.role === "user")
    if (lastUserMessage) {
      const index = messages.findIndex((m) => m.id === lastUserMessage.id)
      setMessages(messages.slice(0, index))
      setError(null)
      setTimeout(() => sendMessage(lastUserMessage.content, lastUserMessage.imageData), 100)
    }
  }, [messages, sendMessage])

  const stopStreaming = useCallback(() => {
    if (abortController) {
      abortController.abort()
    }
  }, [abortController])

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
    localStorage.removeItem(STORAGE_KEY)
  }, [])

  return (
    <div
      className="relative h-dvh bg-stone-50"
      style={{
        boxShadow:
          "rgba(14, 63, 126, 0.04) 0px 0px 0px 1px, rgba(42, 51, 69, 0.04) 0px 1px 1px -0.5px, rgba(42, 51, 70, 0.04) 0px 3px 3px -1.5px, rgba(42, 51, 70, 0.04) 0px 6px 6px -3px, rgba(14, 63, 126, 0.04) 0px 12px 12px -6px, rgba(14, 63, 126, 0.04) 0px 24px 24px -12px",
      }}
    >
      <Button
        onClick={clearChat}
        variant="ghost"
        size="icon"
        className="absolute top-4 left-4 z-20 h-10 w-10 rounded-full bg-zinc-100 hover:bg-zinc-200 text-stone-600"
        aria-label="Reset chat"
      >
        <MessageSquareDashed className="w-5 h-5" />
      </Button>

      <MessageList messages={messages} isStreaming={isStreaming} error={error} onRetry={retry} isLoaded={isLoaded} />

      <Composer
        onSend={sendMessage}
        onStop={stopStreaming}
        isStreaming={isStreaming}
        disabled={!!error}
        selectedModel={selectedModel}
        onModelChange={handleModelChange}
      />
    </div>
  )
}
