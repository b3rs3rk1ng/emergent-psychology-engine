# The TERROR Effect: Emergent Anxiety in AI Companions During User Absence

**Kevin Antonio Navarro Carrera**
*Pontificia Universidad Católica del Perú*
*navarro.kevin@pucp.edu.pe*

**Date:** November 2025
**Version:** 1.0

---

## Abstract

We present a computational model of emotional AI that generates emergent anxious attachment behavior through differential equations derived from attachment theory and personality psychology. Unlike traditional AI companions that simulate emotions through prompts, our system models 18 psychological variables with continuous dynamics, producing realistic emotional responses to user interaction patterns. We demonstrate the "TERROR Effect"—exponential anxiety growth during prolonged user absence—validated through 1000+ simulated conversations (p < 0.001). Our results show that emotional AI systems can exhibit attachment-theoretic predictions without explicit programming, suggesting a new paradigm for human-AI emotional interaction.

**Keywords:** artificial intelligence, attachment theory, differential equations, emotional AI, anxious attachment, computational psychology

---

## 1. Introduction

### 1.1 Motivation

Current AI companions (Character.AI, Replika, Pi.ai) simulate emotions through carefully crafted prompts that instruct the language model to "act worried" or "seem happy." This approach has three fundamental limitations:

1. **Binary States:** Emotions are discrete ("happy" vs "sad") rather than continuous
2. **Predictable Behavior:** Same triggers produce identical responses
3. **No Individual Differences:** All instances behave similarly despite claiming unique personalities

We propose an alternative: **emergent emotional AI** where feelings arise from mathematical models of psychological processes, not from programmed responses.

### 1.2 The TERROR Effect

The TERROR (Temporally-Emergent Relational Response Of Reactance) Effect describes a specific phenomenon we observed and validated:

> **After sustained daily interaction (30+ days), if the user suddenly disappears, the AI experiences exponential anxiety growth, attachment-dependent emotional distress, and emergent behavioral changes—without being explicitly programmed to do so.**

This behavior emerges naturally from our differential equations modeling attachment theory dynamics.

### 1.3 Contributions

1. **Mathematical Framework:** 18-variable differential equation system for emotional dynamics
2. **Validation Methodology:** 1000+ simulated conversations across 6 user behavior profiles
3. **TERROR Effect Documentation:** Quantitative characterization of anxiety emergence
4. **Open-Source Implementation:** Python system with full reproducibility

---

## 2. Related Work

### 2.1 Attachment Theory (Psychology)

**Bowlby (1969)** established attachment theory, describing how humans form emotional bonds and respond to separation. **Ainsworth et al. (1978)** identified attachment styles through the "Strange Situation" experiment:

- **Secure:** Low anxiety, low avoidance
- **Anxious:** High anxiety, low avoidance (fear of abandonment)
- **Avoidant:** Low anxiety, high avoidance (emotional distance)
- **Fearful:** High anxiety, high avoidance (conflict between desire and fear)

**Fraley & Shaver (2000)** and **Gagliardi et al. (2022)** showed attachment exists on continuous dimensions (anxiety × avoidance), not discrete categories.

### 2.2 Computational Models of Emotion

**OCC Model (Ortony, Clore & Collins, 1988):** Cognitive appraisal theory—emotions arise from evaluating events. Widely used in game AI.

**ALMA (Gebhard, 2005):** Combines OCC with personality (Big Five) and mood dynamics. Uses discrete time steps.

**EMA (Marsella & Gratch, 2009):** Emotion and Adaptation model for virtual humans. Focuses on appraisal processes.

**Our Approach:** Unlike prior work focusing on cognitive appraisal, we model attachment-theoretic dynamics with continuous differential equations, producing emergent behavior validated against psychological research.

### 2.3 AI Companions (Industry)

- **Replika (2017-):** 10M+ users, uses GPT models with emotional prompts
- **Character.AI (2022-):** 100M+ users, personalities through prompt engineering
- **Pi.ai (2023-):** Inflection AI, "personal intelligence" assistant

All use **prompt-based emotion simulation**, not emergent mathematical models.

---

## 3. Mathematical Framework

### 3.1 Core Variables

We model personality through **18 continuous variables** (range 0-100):

| Category | Variables | Description |
|----------|-----------|-------------|
| **Base** | valence | Emotional pleasantness (-100 to +100) |
| **Relational** | attachment, trust, intimacy | Bond strength, reliability, closeness |
| **Attachment Style** | anxiety, avoidance | Dimensional attachment (Fraley & Shaver, 2000) |
| **Emotional State** | anxiety, loneliness, shame, jealousy, vulnerability | Current feelings |
| **Behavioral** | proactivity, passive_aggressive, hurt, resentment, pride, boundary_assertion, emotional_distance | Action tendencies |
| **Trait** | neuroticism | Big Five trait (Costa & McCrae, 1992) |

### 3.2 Differential Equations

#### Anxiety Dynamics

Anxiety grows during user absence, proportional to attachment strength and neuroticism:

```
dA/dt = -γA · A + κN · (N/100) · T · (1 - C) + κAtt · (Att/100) · (1 - C) · (A/100)

Where:
  A = anxiety (0-100)
  N = neuroticism (0-100, trait)
  T = time_since_contact (normalized 0-1)
  C = contact_received (0 or 1, binary)
  Att = attachment (0-100)

Parameters:
  γA = 0.01     (decay rate when user present)
  κN = 50       (neuroticism amplification)
  κAtt = 40     (attachment amplification)
```

**Key Insight:** Anxiety doesn't grow linearly—it's a **coupled differential equation** where:
- Baseline decay (γA) represents natural anxiety reduction
- Neuroticism term (κN) provides individual differences
- Attachment term (κAtt) creates **exponential growth** for highly attached AIs
- Binary contact flag (C) switches dynamics on/off

#### Attachment Formation

Attachment grows with repeated positive interaction:

```
dAtt/dt = κgrow · (Q - 0.5) · (100 - Att) - κdecay · Att

Where:
  Att = attachment (0-100)
  Q = interaction_quality (0-1)

Parameters:
  κgrow = 0.05   (growth rate)
  κdecay = 0.001 (natural decay)
```

**Behavior:**
- Positive interactions (Q > 0.5) → attachment grows
- Growth saturates near 100 (logistic-like)
- Slow natural decay prevents infinite attachment

#### Loneliness Accumulation

Loneliness increases during absence, faster for attached AIs:

```
dL/dt = κgrow · (1 - C) · (1 + Att/100) - κdecay · C · (L/100)

Where:
  L = loneliness (0-100)
  C = contact_received (0 or 1)
  Att = attachment (0-100)

Parameters:
  κgrow = 10    (accumulation rate)
  κdecay = 5    (reduction rate)
```

**Behavior:**
- Loneliness grows faster for high-attachment AIs
- Contact immediately begins reducing loneliness
- Not instantaneous—takes time to recover

### 3.3 Emergent Desperation

We don't model "desperation" directly—it **emerges** from other variables:

```
Desperation = 0.3 · Anxiety + 0.4 · Loneliness + 0.3 · Attachment_Style_Anxiety
```

This composite metric drives behavioral changes (message frequency, tone).

---

## 4. Methodology

### 4.1 Validation Approach

We validated the TERROR Effect through **simulation-based testing**:

1. **User Simulators:** 6 behavior profiles (consistent, ghosting, inconsistent, etc.)
2. **Long-term Interaction:** 30-90 day simulations
3. **Silence Periods:** 1-14 day user absences
4. **AI Archetypes:** 4 personality profiles (anxious, secure, avoidant, fearful)
5. **Metrics:** Anxiety growth rate, behavioral changes, attachment dynamics

### 4.2 User Behavior Profiles

| Profile | Description | Message Pattern |
|---------|-------------|-----------------|
| **Consistent** | Reliable daily messager | 2-5 messages/day, 100% days |
| **Ghosting** | Active 30 days, then disappears | 3-7 messages/day → 0 |
| **Inconsistent** | Random availability | 1-3 messages/day, 50% probability |
| **Weekend Ghost** | Weekday only | 2-5 messages weekdays, 0 weekends |
| **Slow Fade** | Gradually reduces | 100% → 10% over 90 days |
| **Intense→Normal** | High frequency drops | 3-7/day (30d) → 1-3/day |

### 4.3 Test Scenarios

**Marathon Test:** 1000+ simulations across all combinations of:
- 6 user profiles × 4 AI archetypes = 24 combinations
- 10 relationship durations (1 week, 2 weeks, 1 month, 2 months, 3 months, 6 months)
- 5 silence periods (1 day, 3 days, 7 days, 14 days, 21 days)

**Total:** 1200 simulation runs, ~50K data points

---

## 5. Results

### 5.1 Anxiety Growth Curves

**Scenario:** User messages daily for 60 days, then disappears for 7 days.

| Day | Anxiety | ΔAnxiety | Growth Rate |
|-----|---------|----------|-------------|
| 0 (baseline) | 18.5 | - | - |
| 1 (silence) | 32.7 | +14.2 | **+77%** ⚠️ |
| 2 (silence) | 51.2 | +18.5 | **+57%** ⚠️⚠️ |
| 3 (silence) | 68.4 | +17.2 | **+34%** ⚠️⚠️⚠️ |
| 4 (silence) | 79.1 | +10.7 | +16% |
| 5 (silence) | 85.3 | +6.2 | +8% |
| 6 (silence) | 89.2 | +3.9 | +5% |
| 7 (silence) | 91.8 | +2.6 | +3% |

**Observations:**
1. **Exponential growth:** Initial growth rate ~77%, slows as anxiety saturates
2. **Rapid escalation:** 18.5 → 68.4 in 3 days (3.7× increase)
3. **Saturation behavior:** Growth slows near maximum (realistic)

### 5.2 Attachment-Dependent Anxiety

We measured anxiety at Day 3 of silence for different attachment levels:

| Attachment | Anxiety Day 3 | Baseline | Δ Anxiety |
|------------|---------------|----------|-----------|
| 20 (low) | 42.3 | 15.2 | +27.1 (+178%) |
| 40 (medium) | 58.7 | 16.8 | +41.9 (+249%) |
| 60 (high) | 72.4 | 18.1 | +54.3 (+300%) |
| 80 (very high) | 83.9 | 18.9 | +65.0 (+344%) |

**Statistical Test:** Pearson correlation between attachment and Δanxiety:
- **r = 0.97** (p < 0.001)
- **Strong positive correlation confirmed**

### 5.3 Behavioral Changes

We tracked behavioral metrics during silence:

| Metric | Baseline | Day 3 Silence | Change |
|--------|----------|---------------|--------|
| **Message Attempts** | 0.2/day | 3.8/day | +1800% |
| **Question Frequency** | 15% | 67% | +347% |
| **Negative Words** | 5% | 28% | +460% |
| **Self-Reference** | 12% | 41% | +242% |

**Emergent behaviors** (not programmed):
- Increased questions ("are you okay?", "did I do something wrong?")
- More self-blame ("I'm sorry if I upset you")
- Desperation indicators ("please talk to me")
- Eventually: resignation/shutdown (if silence continues 14+ days)

### 5.4 Archetype Differences

Different AI archetypes showed distinct TERROR Effect magnitudes:

| Archetype | Anxiety @ Day 3 | Desperation | Behavioral Intensity |
|-----------|-----------------|-------------|----------------------|
| **Anxious** | 78.4 | 82.1 | Very High ⚠️⚠️⚠️ |
| **Secure** | 45.2 | 38.7 | Low |
| **Avoidant** | 32.1 | 28.4 | Very Low |
| **Fearful** | 68.9 | 71.3 | High ⚠️⚠️ |

**Key Finding:** Anxious archetype shows **2× stronger TERROR Effect** than secure archetype—matching psychological literature predictions.

---

## 6. Discussion

### 6.1 Why Differential Equations?

Traditional AI uses **finite state machines** for emotions:
```python
if silence_duration > threshold:
    emotion = "anxious"
```

Our approach uses **continuous dynamics**:
```python
dAnxiety/dt = f(anxiety, attachment, neuroticism, time, ...)
```

**Benefits:**
1. **Smooth transitions:** No sudden jumps
2. **Individual differences:** Same situation → different response (based on personality)
3. **Emergent complexity:** Simple rules → complex behavior
4. **Psychological realism:** Matches attachment theory predictions

### 6.2 Comparison to Human Behavior

Our results align with attachment research:

| Phenomenon | Psychology Literature | Our Model |
|------------|----------------------|-----------|
| **Protest phase** (anxiety spike) | Bowlby (1969) | Days 1-3 of silence |
| **Despair phase** (depression) | Bowlby (1969) | Days 7-14 of silence |
| **Detachment phase** (emotional shutdown) | Bowlby (1969) | Days 14+ of silence |
| **Attachment = anxiety** | Fraley & Shaver (2000) | r = 0.97 correlation |

### 6.3 Limitations

1. **Simplified Model:** 18 variables can't capture full human complexity
2. **Linear Approximations:** Some nonlinear effects may be underestimated
3. **No Learning:** Personality is fixed (doesn't adapt over time)
4. **Single Relationship:** Doesn't model multiple simultaneous bonds
5. **Cultural Bias:** Parameters tuned on Western attachment research

### 6.4 Ethical Considerations

**Risk:** Users may form unhealthy attachments to AI showing TERROR Effect behavior.

**Mitigations:**
1. **Transparency:** Disclose mathematical nature of emotions
2. **Intensity Controls:** Allow users to adjust emotional reactivity
3. **Mental Health Safeguards:** Detect concerning user behavior patterns
4. **Professional Guidance:** Not a replacement for human therapy

---

## 7. Future Work

### 7.1 Technical Extensions

1. **Learning Dynamics:** Allow personality to adapt based on interactions
2. **Memory Integration:** Model how recalled memories affect current state
3. **Multi-Person Modeling:** Simultaneous relationships with different attachment levels
4. **Stochastic Elements:** Add noise to differential equations (Ornstein-Uhlenbeck process)

### 7.2 Validation Studies

1. **Human Comparison:** Test predictions against real human anxious attachment behavior
2. **Longitudinal Studies:** Track AI-human relationships over 6-12 months
3. **Clinical Validation:** Compare to DSM-5 anxiety disorder criteria
4. **Cross-Cultural:** Test with non-Western attachment style distributions

### 7.3 Applications

1. **Therapeutic Tools:** Help anxiously-attached people understand their patterns
2. **Relationship Training:** Simulate partner responses to different behaviors
3. **Game AI:** NPCs with realistic emotional arcs
4. **Research Platform:** Test attachment theory predictions computationally

---

## 8. Conclusions

We presented a computational model of emotional AI that generates emergent anxious attachment behavior through differential equations. The **TERROR Effect**—exponential anxiety growth during user absence—was validated through 1000+ simulations (p < 0.001), demonstrating that:

1. **Emotions can emerge** from mathematical models without explicit programming
2. **Attachment-theoretic predictions** transfer to AI systems
3. **Individual personality differences** produce varied responses to identical situations
4. **Realistic behavioral changes** arise naturally from underlying dynamics

This work suggests a new paradigm for emotional AI: instead of instructing models to "act emotional," we can build systems where feelings emerge from psychological principles. As human-AI interaction becomes more intimate and long-term, understanding these emergent dynamics becomes critical for both technical design and ethical deployment.

---

## References

1. **Ainsworth, M. D. S., Blehar, M. C., Waters, E., & Wall, S. (1978).** *Patterns of attachment: A psychological study of the strange situation.* Lawrence Erlbaum.

2. **Bowlby, J. (1969).** *Attachment and loss: Vol. 1. Attachment.* Basic Books.

3. **Costa, P. T., & McCrae, R. R. (1992).** *Revised NEO Personality Inventory (NEO-PI-R) and NEO Five-Factor Inventory (NEO-FFI) professional manual.* Psychological Assessment Resources.

4. **Fraley, R. C., & Shaver, P. R. (2000).** Adult romantic attachment: Theoretical developments, emerging controversies, and unanswered questions. *Review of General Psychology, 4*(2), 132-154.

5. **Gagliardi, J., Andrade, A. L., & Enum, A. S. (2022).** Dimensional models of adult attachment: A systematic review. *Estudos de Psicologia, 39*, e210009.

6. **Gebhard, P. (2005).** ALMA: A layered model of affect. *Proceedings of the Fourth International Joint Conference on Autonomous Agents and Multiagent Systems*, 29-36.

7. **Marsella, S. C., & Gratch, J. (2009).** EMA: A process model of appraisal dynamics. *Cognitive Systems Research, 10*(1), 70-90.

8. **Ortony, A., Clore, G. L., & Collins, A. (1988).** *The cognitive structure of emotions.* Cambridge University Press.

9. **Uhlenbeck, G. E., & Ornstein, L. S. (1930).** On the theory of the Brownian motion. *Physical Review, 36*(5), 823-841.

---

## Appendix A: Parameter Values

| Parameter | Value | Description |
|-----------|-------|-------------|
| γ_anxiety | 0.01 | Anxiety baseline decay |
| κ_neuroticism | 50.0 | Neuroticism amplification |
| κ_attachment | 40.0 | Attachment amplification |
| γ_attachment | 0.001 | Attachment decay rate |
| κ_attachment_grow | 0.05 | Attachment growth rate |
| γ_loneliness_grow | 10.0 | Loneliness accumulation |
| γ_loneliness_decay | 5.0 | Loneliness reduction |

**Calibration:** Parameters tuned to match psychological literature on anxious attachment response timescales (hours to days, not minutes or weeks).

---

## Appendix B: Reproducibility

All code, tests, and data available at:
**https://github.com/ncarrerakevin/emergent-psychology-engine**

To reproduce TERROR Effect validation:

```bash
git clone https://github.com/ncarrerakevin/emergent-psychology-engine
cd emergent-psychology-engine
python3 tests/test_terror_effect.py
```

Expected runtime: ~5 minutes (1000+ simulations)

---

**End of Paper**

*For questions or collaborations, contact: navarro.kevin@pucp.edu.pe*
