"use client"

import { Warp } from "@paper-design/shaders-react"
import { useState, useEffect, useRef, useCallback } from "react"
import { useAudioLevel } from "@/hooks/use-audio-level"
import { Pane } from "tweakpane"

type Emotion = "joy" | "sadness" | "anger" | "fear" | "disgust" | "anxiety" | "envy" | "boredom" | "embarrassment"

// Helper functions for smooth color interpolation
function hexToRgb(hex: string): [number, number, number] {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return [r, g, b]
}

function rgbToHex(r: number, g: number, b: number): string {
  return `#${Math.round(r).toString(16).padStart(2, "0")}${Math.round(g).toString(16).padStart(2, "0")}${Math.round(b).toString(16).padStart(2, "0")}`
}

function lerpColor(from: string, to: string, t: number): string {
  const [r1, g1, b1] = hexToRgb(from)
  const [r2, g2, b2] = hexToRgb(to)
  return rgbToHex(
    r1 + (r2 - r1) * t,
    g1 + (g2 - g1) * t,
    b1 + (b2 - b1) * t,
  )
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t
}

const TRANSITION_DURATION = 2000 // 2 seconds for smooth transitions

const DEFAULT_PARAMS = {
  proportion: 0.35,
  softness: 0.9,
  distortion: 0.15,
  swirl: 0.5,
  swirlIterations: 0,
  shape: "edge" as "checks" | "stripes" | "edge",
  shapeScale: 0,
  speed: 10,
  scale: 0.31,
  rotation: 176,
  offsetX: 0.65,
  offsetY: 0.09,
  color1: "#FFDF4F",
  color2: "#FFF8D6",
  color3: "#FFB347",
}

const emotions: Record<Emotion, { color1: string; color2: string; color3: string; speed: number; distortion: number; softness: number; swirl: number }> = {
  joy:           { color1: "#FFDF4F", color2: "#FFF8D6", color3: "#FFB347", speed: 10,  distortion: 0.15, softness: 0.9,  swirl: 0.5 },
  sadness:       { color1: "#3B82F6", color2: "#BFDBFE", color3: "#1E40AF", speed: 3,   distortion: 0.10, softness: 1.0,  swirl: 0.2 },
  anger:         { color1: "#EF4444", color2: "#FCA5A5", color3: "#DC2626", speed: 22,  distortion: 0.80, softness: 0.2,  swirl: 0.7 },
  fear:          { color1: "#8B5CF6", color2: "#DDD6FE", color3: "#6D28D9", speed: 18,  distortion: 0.50, softness: 0.5,  swirl: 0.8 },
  disgust:       { color1: "#22C55E", color2: "#BBF7D0", color3: "#15803D", speed: 7,   distortion: 0.40, softness: 0.3,  swirl: 0.3 },
  anxiety:       { color1: "#F97316", color2: "#FED7AA", color3: "#EA580C", speed: 25,  distortion: 0.60, softness: 0.4,  swirl: 0.9 },
  envy:          { color1: "#14B8A6", color2: "#99F6E4", color3: "#0D9488", speed: 9,   distortion: 0.35, softness: 0.5,  swirl: 0.5 },
  boredom:       { color1: "#9CA3AF", color2: "#D1D5DB", color3: "#6B7280", speed: 2,   distortion: 0.05, softness: 0.8,  swirl: 0.1 },
  embarrassment: { color1: "#EC4899", color2: "#FBCFE8", color3: "#DB2777", speed: 14,  distortion: 0.30, softness: 0.7,  swirl: 0.4 },
}

export type { Emotion }
export { emotions }

interface AiOrbProps {
  externalEmotion?: Emotion
}

export function AiOrb({ externalEmotion }: AiOrbProps = {}) {
  const [emotion, setEmotion] = useState<Emotion>("joy")
  const { audioLevel } = useAudioLevel()
  const paneRef = useRef<Pane | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const [params, setParams] = useState({ ...DEFAULT_PARAMS })

  // Animation refs
  const animationRef = useRef<number | null>(null)
  const startTimeRef = useRef<number>(0)
  const fromParamsRef = useRef({
    color1: DEFAULT_PARAMS.color1,
    color2: DEFAULT_PARAMS.color2,
    color3: DEFAULT_PARAMS.color3,
    speed: DEFAULT_PARAMS.speed,
    distortion: DEFAULT_PARAMS.distortion,
    softness: DEFAULT_PARAMS.softness,
    swirl: DEFAULT_PARAMS.swirl,
  })
  const toParamsRef = useRef({ ...fromParamsRef.current })

  useEffect(() => {
    if (!containerRef.current || paneRef.current) return

    const pane = new Pane({
      container: containerRef.current,
      title: "Shader Controls",
      expanded: false,
    })

    const colorsFolder = pane.addFolder({ title: "Colors" })
    colorsFolder.addBinding(params, "color1", { label: "Color 1" })
    colorsFolder.addBinding(params, "color2", { label: "Color 2" })
    colorsFolder.addBinding(params, "color3", { label: "Color 3" })

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

    const commonFolder = pane.addFolder({ title: "Common Props" })
    commonFolder.addBinding(params, "speed", { min: 0, max: 30, step: 0.1 })
    commonFolder.addBinding(params, "scale", { min: 0.01, max: 4, step: 0.01 })
    commonFolder.addBinding(params, "rotation", { min: 0, max: 360, step: 1 })
    commonFolder.addBinding(params, "offsetX", { min: -1, max: 1, step: 0.01 })
    commonFolder.addBinding(params, "offsetY", { min: -1, max: 1, step: 0.01 })

    const exportFolder = pane.addFolder({ title: "Export/Import" })
    exportFolder.addButton({ title: "Copy Values" }).on("click", () => {
      const exportData = JSON.stringify(params, null, 2)
      navigator.clipboard.writeText(exportData)
      alert("Values copied to clipboard!")
    })

    pane.on("change", () => {
      setParams({ ...params })
    })

    paneRef.current = pane

    return () => {
      pane.dispose()
      paneRef.current = null
    }
  }, [])

  // Smooth transition animation using easeInOutCubic
  const animate = useCallback((timestamp: number) => {
    const elapsed = timestamp - startTimeRef.current
    const rawT = Math.min(elapsed / TRANSITION_DURATION, 1)

    // easeInOutCubic for organic feel
    const t = rawT < 0.5
      ? 4 * rawT * rawT * rawT
      : 1 - Math.pow(-2 * rawT + 2, 3) / 2

    const from = fromParamsRef.current
    const to = toParamsRef.current

    const newColor1 = lerpColor(from.color1, to.color1, t)
    const newColor2 = lerpColor(from.color2, to.color2, t)
    const newColor3 = lerpColor(from.color3, to.color3, t)
    const newSpeed = lerp(from.speed, to.speed, t)
    const newDistortion = lerp(from.distortion, to.distortion, t)
    const newSoftness = lerp(from.softness, to.softness, t)
    const newSwirl = lerp(from.swirl, to.swirl, t)

    setParams((prev) => ({
      ...prev,
      color1: newColor1,
      color2: newColor2,
      color3: newColor3,
      speed: newSpeed,
      distortion: newDistortion,
      softness: newSoftness,
      swirl: newSwirl,
    }))

    if (rawT < 1) {
      animationRef.current = requestAnimationFrame(animate)
    } else {
      animationRef.current = null
    }
  }, [])

  const handleEmotionChange = useCallback((e: Emotion) => {
    setEmotion(e)
    const emotionData = emotions[e]

    // Cancel any running animation
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }

    // Snapshot current state as "from"
    setParams((prev) => {
      fromParamsRef.current = {
        color1: prev.color1,
        color2: prev.color2,
        color3: prev.color3,
        speed: prev.speed,
        distortion: prev.distortion,
        softness: prev.softness,
        swirl: prev.swirl,
      }
      return prev
    })

    // Set target
    toParamsRef.current = {
      color1: emotionData.color1,
      color2: emotionData.color2,
      color3: emotionData.color3,
      speed: emotionData.speed,
      distortion: emotionData.distortion,
      softness: emotionData.softness,
      swirl: emotionData.swirl,
    }

    // Start animation
    startTimeRef.current = performance.now()
    animationRef.current = requestAnimationFrame(animate)
  }, [animate])

  // Respond to external emotion changes
  useEffect(() => {
    if (externalEmotion && externalEmotion !== emotion) {
      handleEmotionChange(externalEmotion)
    }
  }, [externalEmotion])

  // Cleanup animation on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [])

  return (
    <div className="relative h-full bg-white flex flex-col items-center justify-center gap-8 overflow-hidden">
      <div ref={containerRef} className="absolute top-4 right-4 z-50 hidden" />

      {/* Emotion selector (hidden - controlled externally) */}
      <div className="flex flex-wrap justify-center gap-2 px-4 hidden">
        {(Object.keys(emotions) as Emotion[]).map((e) => (
          <button
            key={e}
            onClick={() => handleEmotionChange(e)}
            className={`font-sans text-[10px] px-3 py-1 rounded-full transition-colors ${
              emotion === e ? "bg-black text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {e}
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

    </div>
  )
}
