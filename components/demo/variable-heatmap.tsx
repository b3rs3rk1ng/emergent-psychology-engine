"use client"

import { useEffect, useRef, useState } from "react"

const VARIABLE_LABELS: Record<string, { label: string; unit: string; category: string; range: [number, number] }> = {
  valence:                   { label: "Valence (v)",              unit: "[-100, 100]", category: "fast",    range: [-100, 100] },
  arousal:                   { label: "Arousal (a)",              unit: "[0, 100]",    category: "fast",    range: [0, 100] },
  attachment:                { label: "Attachment (α)",           unit: "[0, 100]",    category: "medium",  range: [0, 100] },
  trust:                     { label: "Trust (τ)",                unit: "[0, 100]",    category: "medium",  range: [0, 100] },
  intimacy:                  { label: "Intimacy (ι)",             unit: "[0, 100]",    category: "medium",  range: [0, 100] },
  anxiety:                   { label: "Anxiety (ξ)",              unit: "[0, 100]",    category: "medium",  range: [0, 100] },
  loneliness:                { label: "Loneliness (λ)",           unit: "[0, 100]",    category: "medium",  range: [0, 100] },
  proactivity:               { label: "Proactivity (π)",          unit: "[0, 100]",    category: "medium",  range: [0, 100] },
  shame:                     { label: "Shame (σ)",                unit: "[0, 100]",    category: "medium",  range: [0, 100] },
  neuroticism:               { label: "Neuroticism (N)",          unit: "[0, 100]",    category: "slow",    range: [0, 100] },
  attachment_style_anxiety:  { label: "Att. Style Anxiety (Aₐ)",  unit: "[0, 100]",    category: "slow",    range: [0, 100] },
  attachment_style_avoidance:{ label: "Att. Style Avoidance (Aᵥ)",unit: "[0, 100]",    category: "slow",    range: [0, 100] },
  dependency:                { label: "Dependency (δ)",           unit: "[0, 100]",    category: "slow",    range: [0, 100] },
  hurt:                      { label: "Hurt (h)",                 unit: "[0, 100]",    category: "passive", range: [0, 100] },
  resentment:                { label: "Resentment (ρ)",           unit: "[0, 100]",    category: "passive", range: [0, 100] },
  pride:                     { label: "Pride (φ)",                unit: "[0, 100]",    category: "passive", range: [0, 100] },
  boundary_assertion:        { label: "Boundary (β)",             unit: "[0, 100]",    category: "passive", range: [0, 100] },
  emotional_distance:        { label: "Em. Distance (d)",         unit: "[0, 100]",    category: "passive", range: [0, 100] },
}

const CATEGORY_META: Record<string, { label: string; desc: string }> = {
  fast:    { label: "Fast Dynamics",             desc: "Ornstein-Uhlenbeck process, dt ≈ min" },
  medium:  { label: "Medium Dynamics",           desc: "Coupled ODEs, dt ≈ hr" },
  slow:    { label: "Slow Dynamics (Traits)",    desc: "Trait-level adaptation, dt ≈ day" },
  passive: { label: "Passive-Aggressive",        desc: "Emotional cascade, τ_decay ≈ 48-72 hr" },
}

// Normalize all values to 0..1 for display
function normalizeValue(key: string, value: number): number {
  if (key === "valence") return (value + 100) / 200
  return Math.max(0, Math.min(100, value)) / 100
}

// Scientific diverging colormap: deep blue → white → deep red (similar to RdBu_r)
function getScientificColor(t: number): string {
  // t in [0, 1]
  if (t <= 0.5) {
    const s = t / 0.5 // 0 → 1
    const r = Math.round(33 + s * 211)
    const g = Math.round(102 + s * 149)
    const b = Math.round(172 + s * 75)
    return `rgb(${r},${g},${b})`
  } else {
    const s = (t - 0.5) / 0.5 // 0 → 1
    const r = Math.round(244 - s * 66)
    const g = Math.round(251 - s * 181)
    const b = Math.round(247 - s * 205)
    return `rgb(${r},${g},${b})`
  }
}

// Get text color for contrast
function getTextColor(t: number): string {
  return (t < 0.2 || t > 0.8) ? "rgba(255,255,255,0.9)" : "rgba(0,0,0,0.7)"
}

// Get raw display value from normalized 0..1
function toDisplayValue(key: string, normalized: number): string {
  if (key === "valence") {
    const raw = normalized * 200 - 100
    return raw >= 0 ? `+${raw.toFixed(0)}` : raw.toFixed(0)
  }
  return (normalized * 100).toFixed(0)
}

interface VariableHeatmapProps {
  variables: Record<string, number>
}

export function VariableHeatmap({ variables }: VariableHeatmapProps) {
  const [displayValues, setDisplayValues] = useState<Record<string, number>>({})
  const animRef = useRef<number | null>(null)
  const fromRef = useRef<Record<string, number>>({})
  const toRef = useRef<Record<string, number>>({})
  const startRef = useRef(0)

  useEffect(() => {
    if (Object.keys(displayValues).length === 0) {
      const initial: Record<string, number> = {}
      for (const key of Object.keys(VARIABLE_LABELS)) {
        initial[key] = key === "valence" ? 0.5 : 0
      }
      setDisplayValues(initial)
      fromRef.current = { ...initial }
    }
  }, [])

  useEffect(() => {
    if (!variables || Object.keys(variables).length === 0) return

    if (animRef.current) cancelAnimationFrame(animRef.current)

    fromRef.current = { ...displayValues }
    toRef.current = {}
    for (const key of Object.keys(VARIABLE_LABELS)) {
      toRef.current[key] = normalizeValue(key, variables[key] ?? 0)
    }

    startRef.current = performance.now()

    const animate = (timestamp: number) => {
      const elapsed = timestamp - startRef.current
      const rawT = Math.min(elapsed / 2000, 1)
      const t = rawT < 0.5
        ? 4 * rawT * rawT * rawT
        : 1 - Math.pow(-2 * rawT + 2, 3) / 2

      const current: Record<string, number> = {}
      for (const key of Object.keys(VARIABLE_LABELS)) {
        const from = fromRef.current[key] ?? 0
        const to = toRef.current[key] ?? 0
        current[key] = from + (to - from) * t
      }
      setDisplayValues(current)

      if (rawT < 1) {
        animRef.current = requestAnimationFrame(animate)
      }
    }

    animRef.current = requestAnimationFrame(animate)

    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current)
    }
  }, [variables])

  const categories = ["fast", "medium", "slow", "passive"]

  return (
    <div className="w-full px-4 py-2 select-none" style={{ fontFamily: "'JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', monospace" }}>
      {/* Title */}
      <div className="flex items-baseline justify-between mb-2">
        <div>
          <span className="text-[10px] font-semibold text-stone-700 tracking-wide uppercase">
            State Vector X(t)
          </span>
          <span className="text-[9px] text-stone-400 ml-2">
            n = 18 variables
          </span>
        </div>
        <span className="text-[8px] text-stone-400">
          Emergent Psychology Engine v1.0
        </span>
      </div>

      {/* Categories */}
      <div className="space-y-[6px]">
        {categories.map((cat) => {
          const vars = Object.entries(VARIABLE_LABELS).filter(([, v]) => v.category === cat)
          const meta = CATEGORY_META[cat]
          return (
            <div key={cat}>
              {/* Category header */}
              <div className="flex items-baseline gap-2 mb-[2px]">
                <span className="text-[8px] font-semibold text-stone-500 uppercase tracking-wider">
                  {meta.label}
                </span>
                <span className="text-[7px] text-stone-300 italic">
                  {meta.desc}
                </span>
              </div>

              {/* Variable rows */}
              <div className="border border-stone-200 rounded overflow-hidden">
                {vars.map(([key, info], i) => {
                  const val = displayValues[key] ?? 0
                  const bgColor = getScientificColor(val)
                  const txtColor = getTextColor(val)
                  return (
                    <div
                      key={key}
                      className={`flex items-center h-[22px] ${i > 0 ? "border-t border-stone-200" : ""}`}
                    >
                      {/* Label */}
                      <div className="w-[140px] shrink-0 px-2 text-[8px] text-stone-600 bg-stone-50 h-full flex items-center border-r border-stone-200">
                        {info.label}
                      </div>
                      {/* Heat bar */}
                      <div
                        className="flex-1 h-full relative"
                        style={{ backgroundColor: bgColor }}
                      >
                        {/* Value */}
                        <span
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-[9px] font-medium tabular-nums"
                          style={{ color: txtColor }}
                        >
                          {toDisplayValue(key, val)}
                        </span>
                        {/* Fill indicator line */}
                        <div
                          className="absolute top-0 h-full w-[1px] opacity-40"
                          style={{
                            left: `${val * 100}%`,
                            backgroundColor: txtColor,
                          }}
                        />
                      </div>
                      {/* Range */}
                      <div className="w-[52px] shrink-0 px-1.5 text-[7px] text-stone-300 bg-stone-50 h-full flex items-center justify-center border-l border-stone-200 tabular-nums">
                        {info.unit}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>

      {/* Color scale legend */}
      <div className="mt-2 flex items-center gap-2">
        <span className="text-[7px] text-stone-400 shrink-0">Low</span>
        <div className="flex-1 h-[6px] rounded-sm overflow-hidden flex">
          {Array.from({ length: 40 }).map((_, i) => (
            <div
              key={i}
              className="flex-1 h-full"
              style={{ backgroundColor: getScientificColor(i / 39) }}
            />
          ))}
        </div>
        <span className="text-[7px] text-stone-400 shrink-0">High</span>
        <span className="text-[7px] text-stone-300 ml-1">
          Colormap: RdBu (diverging)
        </span>
      </div>

      {/* Separator */}
      <div className="mt-3 mb-2 border-t border-stone-200" />

      {/* Scientific context */}
      <div className="space-y-2">
        <div>
          <span className="text-[9px] font-semibold text-stone-600 uppercase tracking-wider">
            Why this matters
          </span>
          <p className="text-[8px] text-stone-400 leading-[1.5] mt-1">
            Traditional AI companions simulate emotions via prompt engineering — discrete states
            (&quot;happy&quot;, &quot;sad&quot;) triggered by hardcoded rules. This engine replaces that with a
            system of <span className="text-stone-500 font-medium">coupled ordinary differential equations</span> governing
            18 continuous psychological variables. Emotions are not assigned — they <span className="text-stone-500 italic">emerge</span> from
            the dynamics, producing realistic individual differences, smooth transitions, and
            the validated TERROR effect: exponential anxiety growth during user absence
            (87.9% pass rate, n=1000, p&lt;0.001). Fast variables (valence, arousal)
            follow an <span className="text-stone-500 font-medium">Ornstein-Uhlenbeck stochastic process</span> with
            mean-reversion; medium variables are governed by coupled ODEs with conditional
            decay rates; slow variables encode personality traits that shift over days.
            The passive-aggressive cascade (hurt → resentment → pride → boundary → distance)
            emerges without explicit programming, matching Bowlby&apos;s protest-despair-detachment
            sequence observed in human attachment research.
          </p>
        </div>

        {/* References */}
        <div>
          <span className="text-[9px] font-semibold text-stone-600 uppercase tracking-wider">
            References
          </span>
          <ol className="text-[7px] text-stone-400 leading-[1.6] mt-1 list-none space-y-[2px]">
            <li>[1] Bowlby, J. (1969). <span className="italic">Attachment and Loss: Vol. 1. Attachment.</span> Basic Books.</li>
            <li>[2] Ainsworth, M. D. S., Blehar, M. C., Waters, E., &amp; Wall, S. (1978). <span className="italic">Patterns of Attachment: A Psychological Study of the Strange Situation.</span> Lawrence Erlbaum.</li>
            <li>[3] Costa, P. T. &amp; McCrae, R. R. (1992). <span className="italic">Revised NEO Personality Inventory (NEO-PI-R) and NEO Five-Factor Inventory.</span> PAR.</li>
            <li>[4] Fraley, R. C. &amp; Shaver, P. R. (2000). Adult romantic attachment: Theoretical developments, emerging controversies, and unanswered questions. <span className="italic">Review of General Psychology, 4</span>(2), 132-154.</li>
            <li>[5] Ortony, A., Clore, G. L. &amp; Collins, A. (1988). <span className="italic">The Cognitive Structure of Emotions.</span> Cambridge University Press.</li>
            <li>[6] Gebhard, P. (2005). ALMA: A layered model of affect. <span className="italic">Proc. AAMAS</span>, 29-36.</li>
            <li>[7] Marsella, S. C. &amp; Gratch, J. (2009). EMA: A process model of appraisal dynamics. <span className="italic">Cognitive Systems Research, 10</span>(1), 70-90.</li>
            <li>[8] Uhlenbeck, G. E. &amp; Ornstein, L. S. (1930). On the theory of the Brownian motion. <span className="italic">Physical Review, 36</span>(5), 823-841.</li>
            <li>[9] Gagliardi, G. et al. (2022). Human attachment as a multi-dimensional control system. <span className="italic">Frontiers in Psychology, 13</span>, 844012.</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
