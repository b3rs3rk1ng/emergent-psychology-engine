"use client"

export function TypingIndicator() {
  return (
    <div className="flex gap-3 max-w-[90%] md:max-w-[80%] mr-auto animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-stone-100"
        style={{
          boxShadow:
            "rgba(14, 63, 126, 0.04) 0px 0px 0px 1px, rgba(42, 51, 69, 0.04) 0px 1px 1px -0.5px, rgba(42, 51, 70, 0.04) 0px 3px 3px -1.5px",
        }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#44403c">
          <rect fill="none" height="24" width="24" y="0"/>
          <path d="M20,9V7c0-1.1-0.9-2-2-2h-3c0-1.66-1.34-3-3-3S9,3.34,9,5H6C4.9,5,4,5.9,4,7v2c-1.66,0-3,1.34-3,3c0,1.66,1.34,3,3,3v4 c0,1.1,0.9,2,2,2h12c1.1,0,2-0.9,2-2v-4c1.66,0,3-1.34,3-3C23,10.34,21.66,9,20,9z M7.5,11.5C7.5,10.67,8.17,10,9,10 s1.5,0.67,1.5,1.5S9.83,13,9,13S7.5,12.33,7.5,11.5z M16,17H8v-2h8V17z M15,13c-0.83,0-1.5-0.67-1.5-1.5S14.17,10,15,10 s1.5,0.67,1.5,1.5S15.83,13,15,13z"/>
        </svg>
      </div>

      {/* Typing dots */}
      <div
        className="px-4 py-3 rounded-2xl rounded-bl-md bg-white border border-stone-200"
        style={{
          boxShadow:
            "rgba(14, 63, 126, 0.04) 0px 0px 0px 1px, rgba(42, 51, 69, 0.04) 0px 1px 1px -0.5px, rgba(42, 51, 70, 0.04) 0px 3px 3px -1.5px, rgba(42, 51, 70, 0.04) 0px 6px 6px -3px, rgba(14, 63, 126, 0.04) 0px 12px 12px -6px, rgba(14, 63, 126, 0.04) 0px 24px 24px -12px",
        }}
        role="status"
        aria-label="Assistant is typing"
      >
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-stone-400 animate-bounce" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 rounded-full bg-stone-400 animate-bounce" style={{ animationDelay: "150ms" }} />
          <span className="w-2 h-2 rounded-full bg-stone-400 animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  )
}
