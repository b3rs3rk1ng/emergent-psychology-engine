"use client"

import { useState } from "react"
import { AiOrb } from "@/components/orb/ai-orb"
import type { Emotion } from "@/components/orb/ai-orb"
import { ScenarioPanel } from "@/components/demo/scenario-panel"
import { VariableHeatmap } from "@/components/demo/variable-heatmap"

export default function Home() {
  const [currentEmotion, setCurrentEmotion] = useState<Emotion>("joy")
  const [currentVariables, setCurrentVariables] = useState<Record<string, number>>({})

  const handleScenarioSelect = (emotion: Emotion, variables: Record<string, number>) => {
    setCurrentEmotion(emotion)
    setCurrentVariables(variables)
  }

  return (
    <div className="flex h-dvh">
      {/* Left: Orb + Chat */}
      <div className="w-1/2 h-full flex flex-col border-r border-border">
        <div className="h-[45%] shrink-0">
          <AiOrb externalEmotion={currentEmotion} />
        </div>
        <div className="flex-1 min-h-0 overflow-hidden">
          <ScenarioPanel onScenarioSelect={handleScenarioSelect} />
        </div>
      </div>
      {/* Right: Heatmap */}
      <div className="w-1/2 h-full overflow-y-auto bg-white">
        <VariableHeatmap variables={currentVariables} />
      </div>
    </div>
  )
}
