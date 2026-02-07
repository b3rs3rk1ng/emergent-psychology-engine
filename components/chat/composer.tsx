"use client"

import { useState, useRef, useCallback, type KeyboardEvent, useEffect } from "react"
import { Square, Send } from "lucide-react"
import { cn } from "@/lib/utils"

interface ComposerProps {
  onSend: (content: string, imageData?: string) => void
  onStop: () => void
  isStreaming: boolean
  disabled?: boolean
}

export function Composer({ onSend, onStop, isStreaming, disabled }: ComposerProps) {
  const [value, setValue] = useState("")
  const [hasAnimated, setHasAnimated] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    setHasAnimated(true)
  }, [])

  const handleInput = useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
    }
  }, [])

  const handleSend = useCallback(() => {
    if (!value.trim() || isStreaming || disabled) return
    onSend(value)
    setValue("")
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }
  }, [value, isStreaming, disabled, onSend])

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend],
  )

  return (
    <div className={cn("absolute bottom-4 left-0 right-0 px-4 pointer-events-none z-10", hasAnimated && "composer-intro")}>
      <div className="relative max-w-2xl mx-auto pointer-events-auto">
        <div
          className={cn(
            "flex flex-col gap-3 p-4 bg-white border-stone-200 transition-all duration-200 border-none border-0 overflow-hidden relative rounded-3xl",
            "focus-within:border-stone-300 focus-within:ring-2 focus-within:ring-stone-200",
          )}
          style={{
            boxShadow:
              "rgba(14, 63, 126, 0.06) 0px 0px 0px 1px, rgba(42, 51, 69, 0.06) 0px 1px 1px -0.5px, rgba(42, 51, 70, 0.06) 0px 3px 3px -1.5px, rgba(42, 51, 70, 0.06) 0px 6px 6px -3px, rgba(14, 63, 126, 0.06) 0px 12px 12px -6px, rgba(14, 63, 126, 0.06) 0px 24px 24px -12px",
          }}
        >
          <div className="flex gap-2 items-center">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => {
                setValue(e.target.value)
                handleInput()
              }}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... (Shift+Enter for new line)"
              disabled={isStreaming || disabled}
              rows={1}
              className={cn(
                "flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-stone-800 placeholder:text-stone-400",
                "focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed",
                "max-h-[56px] overflow-y-auto",
              )}
              aria-label="Message input"
            />

            {isStreaming ? (
              <button
                onClick={onStop}
                className="h-9 w-9 shrink-0 transition-all rounded-full flex items-center justify-center cursor-pointer hover:scale-105 bg-red-100 hover:bg-red-200"
                aria-label="Stop generating"
              >
                <Square
                  className="w-4 h-4 text-red-700"
                  fill="currentColor"
                  aria-hidden="true"
                />
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!value.trim() || disabled}
                className={cn(
                  "h-9 w-9 shrink-0 transition-all rounded-full flex items-center justify-center bg-stone-800 hover:bg-stone-900 text-white",
                  !value.trim() || disabled
                    ? "opacity-30 cursor-not-allowed"
                    : "cursor-pointer hover:scale-105",
                )}
                aria-label="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
