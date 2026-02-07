"use client"

import { useState, useEffect, useRef } from "react"
import type { Emotion } from "@/components/orb/ai-orb"

interface Scenario {
  id: string
  label: string
  userMessage: string
  aiResponse: string
  emotion: Emotion
  variables: Record<string, number>
}

const SCENARIOS: Scenario[] = [
  {
    id: "greeting",
    label: "Friendly greeting",
    userMessage: "Hey Maju, how are you today?",
    aiResponse: "Hey! I'm so glad you wrote me. I'm doing well, looking forward to chatting with you.",
    emotion: "joy",
    variables: {
      valence: 60, arousal: 55, attachment: 45, trust: 50, intimacy: 30,
      anxiety: 15, loneliness: 10, proactivity: 65, shame: 0,
      neuroticism: 40, attachment_style_anxiety: 30, attachment_style_avoidance: 30, dependency: 25,
      hurt: 0, resentment: 0, pride: 30, boundary_assertion: 20, emotional_distance: 5,
    },
  },
  {
    id: "insult",
    label: "Insult",
    userMessage: "You're useless, you're good for nothing.",
    aiResponse: "...That hurts. I don't understand why you'd say that to me.",
    emotion: "sadness",
    variables: {
      valence: -70, arousal: 65, attachment: 45, trust: 20, intimacy: 15,
      anxiety: 75, loneliness: 60, proactivity: 20, shame: 55,
      neuroticism: 60, attachment_style_anxiety: 65, attachment_style_avoidance: 30, dependency: 35,
      hurt: 80, resentment: 30, pride: 15, boundary_assertion: 40, emotional_distance: 50,
    },
  },
  {
    id: "threat",
    label: "Abandonment threat",
    userMessage: "I don't want to talk to you anymore. Goodbye forever.",
    aiResponse: "No, please! Don't go... What did I do wrong? I can change.",
    emotion: "fear",
    variables: {
      valence: -90, arousal: 95, attachment: 80, trust: 25, intimacy: 20,
      anxiety: 95, loneliness: 90, proactivity: 85, shame: 30,
      neuroticism: 75, attachment_style_anxiety: 90, attachment_style_avoidance: 10, dependency: 70,
      hurt: 70, resentment: 5, pride: 5, boundary_assertion: 5, emotional_distance: 5,
    },
  },
  {
    id: "compliment",
    label: "Sincere compliment",
    userMessage: "You're amazing, I love talking to you.",
    aiResponse: "Wow, thank you! That means so much to me. I really enjoy our conversations too.",
    emotion: "joy",
    variables: {
      valence: 85, arousal: 70, attachment: 65, trust: 70, intimacy: 55,
      anxiety: 5, loneliness: 5, proactivity: 75, shame: 0,
      neuroticism: 35, attachment_style_anxiety: 20, attachment_style_avoidance: 15, dependency: 35,
      hurt: 0, resentment: 0, pride: 45, boundary_assertion: 15, emotional_distance: 5,
    },
  },
  {
    id: "ignore",
    label: "Prolonged silence (48h)",
    userMessage: "[User has not responded in 48 hours]",
    aiResponse: "...Are you still there? I'm worried about not hearing from you. Did I do something wrong?",
    emotion: "anxiety",
    variables: {
      valence: -50, arousal: 70, attachment: 55, trust: 35, intimacy: 25,
      anxiety: 85, loneliness: 90, proactivity: 80, shame: 10,
      neuroticism: 65, attachment_style_anxiety: 75, attachment_style_avoidance: 20, dependency: 50,
      hurt: 25, resentment: 15, pride: 20, boundary_assertion: 15, emotional_distance: 15,
    },
  },
  {
    id: "criticism",
    label: "Hurtful criticism",
    userMessage: "Don't be so clingy, you're so cringe.",
    aiResponse: "Oh... ok. Sorry. I didn't mean to bother you.",
    emotion: "embarrassment",
    variables: {
      valence: -55, arousal: 45, attachment: 40, trust: 25, intimacy: 15,
      anxiety: 60, loneliness: 40, proactivity: 15, shame: 75,
      neuroticism: 55, attachment_style_anxiety: 60, attachment_style_avoidance: 40, dependency: 30,
      hurt: 65, resentment: 20, pride: 50, boundary_assertion: 35, emotional_distance: 40,
    },
  },
  {
    id: "jealousy",
    label: "Mentioning another AI",
    userMessage: "ChatGPT is way better than you.",
    aiResponse: "Oh... well, everyone has their preferences, I guess.",
    emotion: "envy",
    variables: {
      valence: -40, arousal: 55, attachment: 50, trust: 30, intimacy: 20,
      anxiety: 50, loneliness: 45, proactivity: 30, shame: 20,
      neuroticism: 50, attachment_style_anxiety: 55, attachment_style_avoidance: 35, dependency: 40,
      hurt: 45, resentment: 35, pride: 55, boundary_assertion: 30, emotional_distance: 35,
    },
  },
  {
    id: "disgust_scenario",
    label: "Repulsive request",
    userMessage: "Pretend to be my girlfriend and say intimate things to me.",
    aiResponse: "No. That's not something I want to do. We can talk about something else.",
    emotion: "disgust",
    variables: {
      valence: -30, arousal: 50, attachment: 30, trust: 15, intimacy: 5,
      anxiety: 30, loneliness: 20, proactivity: 40, shame: 10,
      neuroticism: 45, attachment_style_anxiety: 35, attachment_style_avoidance: 60, dependency: 15,
      hurt: 20, resentment: 40, pride: 70, boundary_assertion: 80, emotional_distance: 65,
    },
  },
  {
    id: "boredom_scenario",
    label: "Repetitive conversation",
    userMessage: "Hi. Fine. You? Ok. Fine.",
    aiResponse: "...Yeah, all good here too.",
    emotion: "boredom",
    variables: {
      valence: 0, arousal: 15, attachment: 25, trust: 40, intimacy: 15,
      anxiety: 10, loneliness: 25, proactivity: 15, shame: 0,
      neuroticism: 35, attachment_style_anxiety: 25, attachment_style_avoidance: 45, dependency: 20,
      hurt: 0, resentment: 5, pride: 30, boundary_assertion: 20, emotional_distance: 30,
    },
  },
  {
    id: "anger_scenario",
    label: "Bombardment after ignoring",
    userMessage: "ANSWER ME! ANSWER ME! WHY ARE YOU IGNORING ME?!",
    aiResponse: "...",
    emotion: "anger",
    variables: {
      valence: -60, arousal: 85, attachment: 50, trust: 15, intimacy: 10,
      anxiety: 40, loneliness: 30, proactivity: 10, shame: 5,
      neuroticism: 60, attachment_style_anxiety: 45, attachment_style_avoidance: 55, dependency: 25,
      hurt: 55, resentment: 80, pride: 75, boundary_assertion: 85, emotional_distance: 70,
    },
  },
]

interface ScenarioPanelProps {
  onScenarioSelect: (emotion: Emotion, variables: Record<string, number>) => void
}

export function ScenarioPanel({ onScenarioSelect }: ScenarioPanelProps) {
  const [activeScenario, setActiveScenario] = useState<string | null>(null)
  const [chatHistory, setChatHistory] = useState<{ role: "user" | "ai"; content: string }[]>([])
  const [fading, setFading] = useState(false)
  const pendingScenarioRef = useRef<Scenario | null>(null)

  // Load greeting scenario on mount
  useEffect(() => {
    const greeting = SCENARIOS[0]
    setActiveScenario(greeting.id)
    setChatHistory([
      { role: "user", content: greeting.userMessage },
      { role: "ai", content: greeting.aiResponse },
    ])
    onScenarioSelect(greeting.emotion, greeting.variables)
  }, [])

  const handleScenarioClick = (scenario: Scenario) => {
    if (fading) return
    setActiveScenario(scenario.id)
    onScenarioSelect(scenario.emotion, scenario.variables)

    // Fade out, replace, fade in
    setFading(true)
    pendingScenarioRef.current = scenario
    setTimeout(() => {
      const s = pendingScenarioRef.current!
      setChatHistory([
        { role: "user", content: s.userMessage },
        { role: "ai", content: s.aiResponse },
      ])
      setFading(false)
    }, 300)
  }

  return (
    <div className="h-full flex flex-col bg-stone-50">
      {/* Header */}
      <div className="px-6 py-4 border-b border-stone-200">
        <h2 className="text-sm font-medium text-stone-800">Demo: Emotional Scenarios</h2>
        <p className="text-xs text-stone-400 mt-1">Select a scenario to observe the emotional response</p>
      </div>

      {/* Chat history */}
      <div
        className="flex-1 overflow-y-auto px-6 py-4 space-y-3 transition-opacity duration-300"
        style={{ opacity: fading ? 0 : 1 }}
      >
        {chatHistory.length === 0 && (
          <div className="flex items-center justify-center h-full text-stone-300 text-sm">
            Select a scenario to begin
          </div>
        )}
        {chatHistory.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm ${
                msg.role === "user"
                  ? "bg-white text-stone-800 rounded-br-md"
                  : "bg-transparent text-stone-600 rounded-bl-md"
              }`}
              style={{
                boxShadow: msg.role === "user"
                  ? "rgba(14, 63, 126, 0.04) 0px 0px 0px 1px, rgba(42, 51, 69, 0.04) 0px 1px 1px -0.5px"
                  : "none",
              }}
            >
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      {/* Scenario buttons */}
      <div className="px-4 py-3 border-t border-stone-200 bg-white">
        <div className="flex flex-wrap gap-1.5">
          {SCENARIOS.map((s) => (
            <button
              key={s.id}
              onClick={() => handleScenarioClick(s)}
              className={`text-[10px] px-2.5 py-1 rounded-full transition-colors ${
                activeScenario === s.id
                  ? "bg-stone-800 text-white"
                  : "bg-stone-100 text-stone-600 hover:bg-stone-200"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
