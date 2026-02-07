"use client"

import { Warp } from "@paper-design/shaders-react"
import { useState, useEffect, useRef } from "react"
import { useAudioLevel } from "@/hooks/use-audio-level"
import { Pane } from "tweakpane"

type Theme = "default" | "angsty" | "tibor" | "minty"

const DEFAULT_PARAMS = {
  proportion: 0.35,
  softness: 1,
  distortion: 0.32,
  swirl: 1,
  swirlIterations: 0,
  shape: "edge" as "checks" | "stripes" | "edge",
  shapeScale: 0,
  speed: 12.2,
  scale: 0.31,
  rotation: 176,
  offsetX: 0.65,
  offsetY: 0.09,
  color1: "#ade7ff",
  color2: "#ebf4ff",
  color3: "#00bbff",
}

const themes: Record<Theme, { color1: string; color2: string; color3: string }> = {
  default: { color1: "#ade7ff", color2: "#ebf4ff", color3: "#00bbff" },
  angsty: { color1: "#ffffff", color2: "#bfbfbf", color3: "#ffffff" },
  tibor: { color1: "#ff6f00", color2: "#fec398", color3: "#ffffff" },
  minty: { color1: "#00c853", color2: "#98fec3", color3: "#ffffff" },
}

const themeLabels: Record<Theme, string> = {
  default: "default",
  angsty: "angsty teen",
  tibor: "hello tibor",
  minty: "minty fresh",
}

export function AiOrb() {
  const [theme, setTheme] = useState<Theme>("default")
  const { audioLevel, isListening, startListening, stopListening } = useAudioLevel()
  const paneRef = useRef<Pane | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const [params, setParams] = useState({ ...DEFAULT_PARAMS })

  useEffect(() => {
    if (!containerRef.current || paneRef.current) return

    const pane = new Pane({
      container: containerRef.current,
      title: "Shader Controls",
    })

    // Colors folder
    const colorsFolder = pane.addFolder({ title: "Colors" })
    colorsFolder.addBinding(params, "color1", { label: "Color 1" })
    colorsFolder.addBinding(params, "color2", { label: "Color 2" })
    colorsFolder.addBinding(params, "color3", { label: "Color 3" })

    // Shader props folder
    const shaderFolder = pane.addFolder({ title: "Shader Props" })
    shaderFolder.addBinding(params, "proportion", { min: 0, max: 1, step: 0.01 })
    shaderFolder.addBinding(params, "softness", { min: 0, max: 1, step: 0.01 })
    shaderFolder.addBinding(params, "distortion", { min: 0, max: 1, step: 0.01 })
    shaderFolder.addBinding(params, "swirl", { min: 0, max: 1, step: 0.01 })
    shaderFolder.addBinding(params, "swirlIterations", { min: 0, max: 20, step: 1 })
    shaderFolder.addBinding(params, "shape", {
      options: { checks: "checks", stripes: "stripes", edge: "edge" },
    })
    shaderFolder.addBinding(params, "shapeScale", { min: 0, max: 1, step: 0.01 })

    // Common props folder
    const commonFolder = pane.addFolder({ title: "Common Props" })
    commonFolder.addBinding(params, "speed", { min: 0, max: 30, step: 0.1 })
    commonFolder.addBinding(params, "scale", { min: 0.01, max: 4, step: 0.01 })
    commonFolder.addBinding(params, "rotation", { min: 0, max: 360, step: 1 })
    commonFolder.addBinding(params, "offsetX", { min: -1, max: 1, step: 0.01 })
    commonFolder.addBinding(params, "offsetY", { min: -1, max: 1, step: 0.01 })

    // Copy/Paste folder
    const exportFolder = pane.addFolder({ title: "Export/Import" })
    exportFolder.addButton({ title: "Copy Values" }).on("click", () => {
      const exportData = JSON.stringify(params, null, 2)
      navigator.clipboard.writeText(exportData)
      alert("Values copied to clipboard! Paste them to v0 to update defaults.")
    })

    // Listen for changes
    pane.on("change", () => {
      setParams({ ...params })
    })

    paneRef.current = pane

    return () => {
      pane.dispose()
      paneRef.current = null
    }
  }, [])

  const handleThemeChange = (t: Theme) => {
    setTheme(t)
    const themeColors = themes[t]
    params.color1 = themeColors.color1
    params.color2 = themeColors.color2
    params.color3 = themeColors.color3
    setParams({ ...params })
    paneRef.current?.refresh()
  }

  const handleCall = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center gap-8">
      <div ref={containerRef} className="fixed top-4 right-4 z-50" />

      {/* Theme selector */}
      <div className="flex gap-2">
        {(Object.keys(themes) as Theme[]).map((t) => (
          <button
            key={t}
            onClick={() => handleThemeChange(t)}
            className={`font-sans text-[10px] px-3 py-1 rounded-full transition-colors ${
              theme === t ? "bg-black text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {themeLabels[t]}
          </button>
        ))}
      </div>

      {/* AI Orb - circular clipped shader */}
      <div
        className="rounded-full overflow-hidden"
        style={{
          width: 280,
          height: 280,
          transform: `scale(${1 + audioLevel * 0.15})`,
          transition: "transform 50ms ease-out",
        }}
      >
        <Warp
          width={280}
          height={280}
          colors={[params.color1, params.color2, params.color3]}
          proportion={params.proportion}
          softness={params.softness}
          distortion={params.distortion}
          swirl={params.swirl}
          swirlIterations={params.swirlIterations}
          shape={params.shape}
          shapeScale={params.shapeScale}
          speed={params.speed}
          scale={params.scale}
          rotation={params.rotation}
          offsetX={params.offsetX}
          offsetY={params.offsetY}
        />
      </div>

      {/* Call button */}
      <button
        onClick={handleCall}
        className={`font-sans text-[10px] px-2.5 py-1 rounded transition-colors ${
          isListening ? "bg-black text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
        }`}
      >
        {isListening ? "end call" : "call me"}
      </button>
    </div>
  )
}
