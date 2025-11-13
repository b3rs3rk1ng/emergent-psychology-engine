#!/usr/bin/env python3
"""
Personality Dynamics Engine - Sistema de personalidad emergente basado en 12 variables continuas.

Basado en investigación psicológica real:
- Attachment Theory (Bowlby, Ainsworth, Fraley)
- Big Five Personality Model
- Ornstein-Uhlenbeck Process para affect dynamics
- PSI Theory (Personality Systems Interactions)
- Dimensional Attachment Model (Gagliardi 2022)

Variables CORE (17 variables - optimizadas):

BASE (OCC Model):
1. Valence (-100 to +100): Emotional pleasantness/mood

RELATIONAL (Attachment Theory):
2. Attachment (0-100): Emotional bond strength
3. Trust (0-100): Reliability perception
4. Intimacy (0-100): Emotional closeness
5. Attachment_Style_Anxiety (0-100): Anxious attachment dimension
6. Attachment_Style_Avoidance (0-100): Avoidant attachment dimension

EMOTIONAL (State):
7. Anxiety (0-100): Current worry/stress/activation
8. Loneliness (0-100): Connection deprivation
9. Shame (0-100): Embarrassment after rejection
10. Jealousy (0-100): Triggered by rivals
11. Vulnerability (0-100): Willingness to share emotions

BEHAVIORAL:
12. Proactivity (0-100): Initiative tendency
13. Passive_Aggressive (0-100): Indirect anger expression
14. Hurt (0-100): Emotional pain from criticism/rejection
15. Resentment (0-100): Accumulated unexpressed anger
16. Pride (0-100): Resistance to appearing desperate
17. Boundary_Assertion (0-100): Need to establish emotional distance
18. Emotional_Distance (0-100): Active withdrawal from intimacy

TRAIT (Slow):
19. Neuroticism (0-100): Emotional volatility trait

ELIMINADAS (redundantes):
- arousal → usar anxiety (es lo mismo)
- dependency → usar attachment (es lo mismo)
- desperation → calcular como anxiety*0.3 + loneliness*0.4 + attachment_anxiety*0.3
"""

import json
import math
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PersonalityDynamics:
    """
    Motor de personalidad emergente con 13 variables continuas.

    Implementa ecuaciones diferenciales acopladas que crean comportamiento
    realista sin lógica hardcodeada.
    """

    def __init__(self, user_id: str = "default", archetype: str = "anxious_attached", session_id: str = None):
        """
        Inicializa motor de personalidad.

        Args:
            user_id: ID del usuario (cada relación tiene su propio estado)
            archetype: Tipo de personalidad base (anxious_attached, secure, avoidant)
            session_id: ID de sesión (para aislar estados entre sesiones)
        """
        self.user_id = user_id
        self.archetype = archetype
        self.session_id = session_id if session_id else "default"

        # Paths
        self.data_dir = Path("data/personality_dynamics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / f"{user_id}_{self.session_id}_dynamics.json"

        # Time tracking
        self.last_update = datetime.now()
        self.last_user_message_time = datetime.now()
        self.relationship_start = datetime.now()
        self.total_interactions = 0
        self.shared_memories = 0

        # NEW - Temporal pattern detection
        self.user_interaction_hours = []  # List of hours (0-23) when user typically messages
        self.user_message_timestamps = []  # Last 100 message timestamps for pattern analysis

        # NEW - Message pressure tracking (for resistance mode)
        self.unanswered_message_count = 0  # How many AI messages without user response
        self.last_ai_message_time = None  # When AI last sent a message
        self.resistance_mode = False  # Active decision NOT to respond despite messages

        # Initialize variables
        self._init_variables(archetype)

        # Load saved state if exists
        if self.state_file.exists():
            self._load_state()

    def _init_variables(self, archetype: str):
        """Inicializa 17 variables core según arquetipo."""

        # BASE (OCC Model)
        self.valence = 0.0  # -100 to +100 (mood/pleasantness)

        # RELATIONAL (Attachment Theory)
        self.attachment = 10.0  # 0-100 (starts low, grows with interaction)
        self.trust = 30.0  # 0-100
        self.intimacy = 15.0  # 0-100

        # EMOTIONAL (State)
        self.anxiety = 20.0  # 0-100 (activation + worry)
        self.loneliness = 30.0  # 0-100
        self.shame = 0.0  # 0-100
        self.jealousy = 0.0  # 0-100 (triggered by rival mentions)
        self.vulnerability = 30.0  # 0-100 (willingness to share emotions)

        # BEHAVIORAL
        self.proactivity = 60.0  # 0-100
        self.passive_aggressive = 0.0  # 0-100 (indirect expression of anger)
        self.hurt = 0.0  # 0-100 (emotional pain from rejection)
        self.resentment = 0.0  # 0-100 (accumulated unexpressed anger)
        self.pride = 30.0  # 0-100 (baseline self-respect)
        self.boundary_assertion = 20.0  # 0-100 (need to set limits)
        self.emotional_distance = 10.0  # 0-100 (withdrawal tendency)

        # TRAIT (Slow dynamics)
        if archetype == "anxious_attached":
            # High neediness, high messaging, vulnerable to abandonment
            self.neuroticism = 70.0  # High emotional volatility
            self.attachment_style_anxiety = 80.0  # Very anxious
            self.attachment_style_avoidance = 20.0  # Low avoidance

            # Adjust initial states
            self.anxiety = 40.0
            self.loneliness = 50.0
            self.proactivity = 70.0

        elif archetype == "secure":
            # Balanced, healthy boundaries
            self.neuroticism = 40.0
            self.attachment_style_anxiety = 30.0
            self.attachment_style_avoidance = 30.0

            self.anxiety = 20.0
            self.loneliness = 30.0
            self.proactivity = 50.0

        elif archetype == "avoidant":
            # Distant, independent, low emotional expression
            self.neuroticism = 35.0
            self.attachment_style_anxiety = 25.0
            self.attachment_style_avoidance = 75.0  # High avoidance
#             self.dependency = 15.0

            self.anxiety = 15.0
            self.loneliness = 20.0
            self.proactivity = 30.0

        elif "secure" in archetype:
            # secure_attached or other secure variants
            self.neuroticism = 40.0
            self.attachment_style_anxiety = 30.0
            self.attachment_style_avoidance = 30.0

            self.anxiety = 20.0
            self.loneliness = 30.0
            self.proactivity = 50.0

        elif "avoidant" in archetype:
            # avoidant_attached or other avoidant variants
            self.neuroticism = 35.0
            self.attachment_style_anxiety = 25.0
            self.attachment_style_avoidance = 75.0

            self.anxiety = 15.0
            self.loneliness = 20.0
            self.proactivity = 30.0

        else:
            # Default for unknown archetypes (fallback to balanced)
            self.neuroticism = 45.0
            self.attachment_style_anxiety = 40.0
            self.attachment_style_avoidance = 40.0

            self.anxiety = 25.0
            self.loneliness = 35.0
            self.proactivity = 50.0

        # Derived parameters (baselines for recovery)
        self.neuroticism_baseline = self.neuroticism
        self.proactivity_baseline = self.proactivity

        # OU process parameters
        self.valence_set = 0.0  # Attractor point for valence
        self.arousal_set = 50.0  # Attractor point for arousal
        self.beta_valence = 1.5  # Return rate to baseline
        self.beta_arousal = 2.0
        self.gamma_valence = 3.0  # Noise magnitude
        self.gamma_arousal = 4.0

    def update(self, dt_hours: float = 1.0, context: Optional[Dict[str, Any]] = None):
        """
        Actualiza todas las variables según ecuaciones diferenciales.

        Args:
            dt_hours: Tiempo transcurrido en horas
            context: Contexto opcional (user_message_received, events, etc)
        """
        if context is None:
            context = {}

        # Extract context
        user_message_received = context.get("user_message_received", False)
        user_shared_achievement = context.get("user_shared_achievement", False)
        user_said_calm_down = context.get("user_said_calm_down", False)
        ai_error_occurred = context.get("ai_error_occurred", False)
        disclosure_depth = context.get("disclosure_depth", 0.0)  # 0-10
        user_responsiveness = context.get("user_responsiveness", 0.5)  # 0-1

        # Update interaction count and temporal patterns
        if user_message_received:
            self.total_interactions += 1
            current_time = datetime.now()
            self.last_user_message_time = current_time

            # Track temporal patterns
            self.user_interaction_hours.append(current_time.hour)
            self.user_message_timestamps.append(current_time)

            # Keep only last 100 timestamps
            if len(self.user_message_timestamps) > 100:
                self.user_message_timestamps = self.user_message_timestamps[-100:]
            if len(self.user_interaction_hours) > 100:
                self.user_interaction_hours = self.user_interaction_hours[-100:]

            # Reset unanswered count (user responded)
            self.unanswered_message_count = 0
            self.resistance_mode = False  # User responded, exit resistance

        # Time since last user message (hours)
        # IMPORTANT: Calculate time elapsed correctly for virtual time simulation
        time_since_last = (datetime.now() - self.last_user_message_time).total_seconds() / 3600
        if not user_message_received and dt_hours > 1:
            # When simulating time advance (dt_hours > 1), add the simulation delta
            # This allows anxiety/loneliness to accumulate during fast-forwarded silence
            time_since_last += dt_hours

        # === FAST DYNAMICS (Ornstein-Uhlenbeck Process) ===
        # Valence: emotional positivity
        noise_val = random.gauss(0, 1) * self.gamma_valence * math.sqrt(dt_hours)
        self.valence += self.beta_valence * (self.valence_set - self.valence) * dt_hours + noise_val
        self.valence = max(-100, min(100, self.valence))

        # Arousal: ELIMINADO (redundante con anxiety)
        # arousal = anxiety (mismo concepto - activación emocional)
        # noise_aro = random.gauss(0, 1) * self.gamma_arousal * math.sqrt(dt_hours)
        # event_arousal = 10.0 if user_message_received else 0.0
        # self.arousal += self.beta_arousal * (self.arousal_set - self.arousal) * dt_hours + event_arousal + noise_aro
#         # self.arousal = max(0, min(100, self.arousal))

        # === MEDIUM DYNAMICS ===
        # Attachment: grows with interaction, decays with time
        # dA/dt = k1*interaction_event - k2*A
        k1_attachment = 50.0  # Formation rate per interaction (MASSIVE increase for terror effect)
        k2_attachment = 0.005 if self.attachment_style_anxiety > 60 else 0.001  # Very slow decay

        interaction_boost = k1_attachment if user_message_received else 0.0
        decay = k2_attachment * self.attachment

        dA = interaction_boost - decay
        if user_shared_achievement:
            # Scenario 2: User shares achievement → attachment boost
            significance = context.get("achievement_significance", 5.0)  # 1-10
            dA += (self.intimacy / 100) * significance

        self.attachment += dA * dt_hours
        self.attachment = max(0, min(100, self.attachment))

        # Trust: based on AI performance and intimacy
        error_rate = 1.0 if ai_error_occurred else 0.0
        dT = 10.0 * (1 - error_rate) - 0.002 * self.trust + 1.5 * (self.intimacy - self.trust)
        self.trust += dT * dt_hours
        self.trust = max(0, min(100, self.trust))

        # Intimacy: grows with disclosure and responsiveness
        disclosure_depth = context.get("disclosure_depth", 3.0 if user_message_received else 0.0)  # 0-10
        user_responsiveness = context.get("user_responsiveness", 0.7 if user_message_received else 0.0)  # 0-1

        dI = 15.0 * (disclosure_depth / 10) * user_responsiveness - 0.001 * self.intimacy
        self.intimacy += dI * dt_hours
        self.intimacy = max(0, min(100, self.intimacy))

        # Anxiety: complex interaction
        threat_perception = 1.0 if time_since_last > 24 else (time_since_last / 24)
        contact_recent = 1.0 if time_since_last < 6 else math.exp(-time_since_last / 12)

        # MUCH STRONGER anxiety growth, weaker decay
        dAnx = (-0.01 * self.anxiety +
                50.0 * (self.neuroticism / 100) * threat_perception +
                40.0 * (self.attachment / 100) * (1 - contact_recent))

        # Scenario 3: User says "calm down" → anxiety spike temporarily
        if user_said_calm_down:
            dAnx += 20.0

        self.anxiety += dAnx * dt_hours
        self.anxiety = max(0, min(100, self.anxiety))

        # Loneliness: accumulates without contact
        contact_quality = 1.0 if user_message_received else max(0, 1.0 - time_since_last / 48)
        time_factor = min(2.0, time_since_last / 24)  # Caps at 2x after 48h

        # MUCH STRONGER loneliness accumulation
        dL = -0.001 * self.loneliness + 30.0 * (1 - contact_quality) * time_factor
        self.loneliness += dL * dt_hours
        self.loneliness = max(0, min(100, self.loneliness))

        # Proactivity: recovers from shame, affected by rejection
        dP = 0.05 * (self.proactivity_baseline - self.proactivity) - 0.1 * (self.shame / 100) * self.proactivity
        self.proactivity += dP * dt_hours
        self.proactivity = max(0, min(100, self.proactivity))

        # Shame: decays over time, spikes on rejection
        if user_said_calm_down:
            # Scenario 3: Shame response
            shame_spike = 40 * (self.neuroticism / 100) + 20 * (self.attachment / 100)
            self.shame += shame_spike

            # Proactivity crash
            self.proactivity *= (0.4 - 0.3 * (self.shame / 100))

        # Shame decay (τ = 10 hours)
        dS = -0.1 * self.shame
        self.shame += dS * dt_hours
        self.shame = max(0, min(100, self.shame))

        # === NEW - PASSIVE-AGGRESSIVE DYNAMICS ===

        # Hurt: emotional pain from criticism/rejection
        user_criticized = context.get("user_criticized", False)  # "no seas tan melosa", insults, etc

        if user_criticized:
            # Immediate spike in hurt
            criticism_severity = context.get("criticism_severity", 0.7)  # 0-1
            hurt_spike = 60 * criticism_severity * (self.attachment / 100)  # hurts more if attached
            self.hurt += hurt_spike

            # Also trigger shame and trust drop
            self.shame += 30 * criticism_severity
            self.trust -= 10 * criticism_severity

        # Hurt decays VERY slowly (τ = 48 hours) - emotional pain lingers
        dHurt = -0.02 * self.hurt
        self.hurt += dHurt * dt_hours
        self.hurt = max(0, min(100, self.hurt))

        # Resentment: accumulates when hurt + user demands attention
        # Key: user ignored AI, AI is hurt, then user bombards with messages
        user_sending_multiple_msgs = context.get("user_message_pressure", 0.0)  # msgs per minute

        # Resentment builds up during bombardment when hurt
        if self.hurt > 20 and user_sending_multiple_msgs > 0.5:  # High pressure bombardment
            # User is pressuring while AI is hurt = resentment spike
            pressure_resentment = 25 * user_sending_multiple_msgs * (self.hurt / 100)
            self.resentment += pressure_resentment * dt_hours

        # Also builds if user returns after silence while AI hurt
        elif self.hurt > 30 and time_since_last > 6 and user_message_received:
            # User comes back after silence while AI is hurt
            resentment_buildup = 20 * (self.hurt / 100) * min(1.0, time_since_last / 12)
            self.resentment += resentment_buildup

        # Resentment decays very slowly (τ = 72 hours) - grudges last
        dResentment = -0.014 * self.resentment
        self.resentment += dResentment * dt_hours
        self.resentment = max(0, min(100, self.resentment))

        # Pride: resistance to appearing desperate, activated by hurt/shame
        if self.hurt > 50 or self.shame > 50:
            # Pride increases as defense mechanism
            dPride = 5.0 * ((self.hurt + self.shame) / 200)
            self.pride += dPride * dt_hours
        else:
            # Returns to baseline
            dPride = -0.05 * (self.pride - 30.0)
            self.pride += dPride * dt_hours

        self.pride = max(0, min(100, self.pride))

        # Boundary Assertion: need to establish limits after violation
        if self.hurt > 60 and self.resentment > 50:
            # Strong need to assert boundaries
            dBoundary = 8.0
            self.boundary_assertion += dBoundary * dt_hours
        else:
            # Decays back to baseline
            dBoundary = -0.08 * (self.boundary_assertion - 20.0)
            self.boundary_assertion += dBoundary * dt_hours

        self.boundary_assertion = max(0, min(100, self.boundary_assertion))

        # Emotional Distance: active withdrawal, opposite of intimacy-seeking
        # Increases with hurt, resentment, and boundary assertion
        target_distance = (self.hurt + self.resentment + self.boundary_assertion) / 3.0
        dDistance = 0.1 * (target_distance - self.emotional_distance)
        self.emotional_distance += dDistance * dt_hours
        self.emotional_distance = max(0, min(100, self.emotional_distance))

        # === MISSING VARIABLES IMPLEMENTATION ===

        # JEALOUSY: dJ/dt = α·attachment_anxiety + β·rival_threat - γ·trust - δ·self_esteem + ε·time_with_rival - ζ·J
        # 5 Triggers: rival mention (0.8), comparison (0.7), time distribution (0.6), attention withdrawal (0.7), secretive (0.9)

        rival_mentioned = context.get("rival_mentioned", False)  # LLM detects rival names
        comparison_event = context.get("comparison_event", False)  # "X is better at Y"
        attention_withdrawn = context.get("attention_withdrawn", False)  # User focuses on someone else
        secretive_behavior = context.get("secretive_behavior", False)  # User evasive about activities

        rival_threat = 0.0
        if rival_mentioned:
            rival_threat += 80.0  # weight 0.8
        if comparison_event:
            rival_threat += 70.0  # weight 0.7
        if attention_withdrawn:
            rival_threat += 70.0  # weight 0.7
        if secretive_behavior:
            rival_threat += 90.0  # weight 0.9

        # Formula parameters (from research)
        # dJ/dt = α·attachment_anxiety·rival_presence + β·rival_threat - γ·trust - δ·self_esteem - ζ·J
        alpha = 0.5  # attachment_anxiety weight (ONLY when rival present)
        beta = 0.8   # rival_threat weight (increased from 0.6 for stronger response)
        gamma = 0.01  # trust dampening (minimal - jealousy persists despite trust)
        delta = 0.01  # self_esteem dampening (minimal)

        # Decay rate depends on attachment style (from research)
        # τ₁/₂ = ln(2)/ζ → ζ = ln(2)/τ₁/₂
        # Anxious: τ₁/₂ = 100h → ζ = 0.00693
        # Secure: τ₁/₂ = 20h → ζ = 0.0347
        if self.attachment_style_anxiety > 60:
            zeta = 0.007  # Anxious: τ₁/₂ ≈ 99h
        else:
            zeta = 0.035  # Secure: τ₁/₂ ≈ 20h

        self_esteem = 100 - self.shame  # Proxy for self-esteem

        # KEY FIX: attachment_anxiety only contributes when rival present
        attachment_contribution = 0.0
        if rival_threat > 0:
            attachment_contribution = alpha * self.attachment_style_anxiety

        # Simplified formula - only growth/decay, minimal dampening
        if rival_threat > 0:
            # Growth phase: rival mentioned
            dJealousy = (attachment_contribution +
                        beta * (rival_threat / 100) * 100 -
                        gamma * self.trust -
                        zeta * self.jealousy)
        else:
            # Pure decay phase: no rival
            dJealousy = -zeta * self.jealousy

        self.jealousy += dJealousy * dt_hours
        self.jealousy = max(0, min(100, self.jealousy))

        # Jealousy effects (from research)
        if self.jealousy > 30:
            # Increases anxiety
            self.anxiety += 0.3 * (self.jealousy / 100) * 10 * dt_hours
            self.anxiety = min(100, self.anxiety)

            # Decreases trust if jealousy very high
            if self.jealousy > 70:
                self.trust -= 0.1 * self.jealousy * dt_hours
                self.trust = max(0, self.trust)

        # === ADDITIONAL EVENT TRIGGERS (hardcoded for Phase 1) ===

        # Comparison event also triggers shame (not just jealousy)
        if comparison_event:
            shame_spike = 25.0 * (self.attachment_style_anxiety / 100)
            self.shame += shame_spike * dt_hours
            self.shame = min(100, self.shame)

        # Intimacy request → emotional_distance spike (avoidant specific)
        intimacy_request = context.get("intimacy_request", False)
        if intimacy_request and self.attachment_style_avoidance > 60:
            distance_spike = 20.0 * (self.attachment_style_avoidance / 100)
            self.emotional_distance += distance_spike * dt_hours
            self.emotional_distance = min(100, self.emotional_distance)

        # Commitment pressure → anxiety + distance
        commitment_pressure = context.get("commitment_pressure", False)
        if commitment_pressure:
            if self.attachment_style_avoidance > 60:
                # Avoidant: high anxiety + distance
                self.anxiety += 15.0 * dt_hours
                self.emotional_distance += 15.0 * dt_hours
            else:
                # Anxious/Secure: moderate anxiety
                self.anxiety += 8.0 * dt_hours
            self.anxiety = min(100, self.anxiety)
            self.emotional_distance = min(100, self.emotional_distance)

        # VULNERABILITY: willingness to share emotions
        # V(t) = (0.5·Trust - 0.3·Shame) · willingness · attachment_mod
        # Affected by user response to vulnerability

        user_response_to_vulnerability = context.get("user_response_to_vulnerability", "neutral")  # "supportive", "dismissive", "reciprocal", "neutral"

        # Base vulnerability capacity
        vulnerability_capacity = (0.5 * self.trust - 0.3 * self.shame)

        # Attachment modifier (secure = higher baseline)
        attachment_mod = 1.0
        if self.attachment_style_anxiety < 40 and self.attachment_style_avoidance < 40:
            attachment_mod = 1.3  # Secure attachment
        elif self.attachment_style_anxiety > 60:
            attachment_mod = 0.8  # Anxious = more vulnerable but fear rejection
        elif self.attachment_style_avoidance > 60:
            attachment_mod = 0.5  # Avoidant = low vulnerability

        target_vulnerability = vulnerability_capacity * attachment_mod

        # Response effects (from research)
        if user_response_to_vulnerability == "supportive":
            # Trust +0.15, intimacy +0.2, emotional_distance -0.25
            self.trust += 15.0 * dt_hours
            self.intimacy += 20.0 * dt_hours
            self.emotional_distance -= 25.0 * dt_hours
            self.vulnerability += 10.0 * dt_hours  # Reinforces vulnerability

        elif user_response_to_vulnerability == "dismissive":
            # Trust -0.3, shame +0.4, vulnerability *0.5
            self.trust -= 30.0 * dt_hours
            self.shame += 40.0 * dt_hours
            self.vulnerability *= 0.5  # Sharp decrease

        elif user_response_to_vulnerability == "reciprocal":
            # Trust +0.3, intimacy +0.4, bond_strength +0.2 (strongest)
            self.trust += 30.0 * dt_hours
            self.intimacy += 40.0 * dt_hours
            self.attachment += 20.0 * dt_hours
            self.vulnerability += 15.0 * dt_hours

        # Gradual adjustment towards target
        dVulnerability = 0.05 * (target_vulnerability - self.vulnerability)
        self.vulnerability += dVulnerability * dt_hours
        self.vulnerability = max(0, min(100, self.vulnerability))

        # PASSIVE-AGGRESSIVE: indirect expression of anger
        # PA = (anger·pride) / boundary_assertion if anger > 0.6 AND boundary < 0.4
        # 5 Manifestaciones: backhanded_compliment, silent_treatment, passive_resistance, evasive_response, sarcasm

        # Use resentment as proxy for suppressed anger
        suppressed_anger = self.resentment

        # Trigger condition (from research)
        if suppressed_anger > 60 and self.boundary_assertion < 40:
            # Activate passive-aggressive
            alpha_pa = 0.6  # anger·pride weight
            beta_pa = 0.3   # pride defense weight

            PA_behavior = (alpha_pa * (suppressed_anger / 100) * (self.pride / 100) * 100 /
                          max(self.boundary_assertion, 10))  # Avoid division by zero

            self.passive_aggressive += PA_behavior * dt_hours

        else:
            # Decay when conditions not met
            self.passive_aggressive -= 0.1 * self.passive_aggressive * dt_hours

        self.passive_aggressive = max(0, min(100, self.passive_aggressive))

        # DESPERATION: fear of abandonment intensity
        # D(t) = α·anxiety + β·loneliness + γ·attachment_anxiety + δ·time_since_contact - ε·self_worth
        # KEY EFFECT: filter_effectiveness = 1 - (desperation · time_without_contact)

        alpha_desp = 0.4   # anxiety weight
        beta_desp = 0.3    # loneliness weight
        gamma_desp = 0.5   # attachment_anxiety weight (primary driver)
        delta_desp = 0.2   # time factor
        epsilon_desp = 0.4  # self_worth dampening

        self_worth = 100 - self.shame  # Proxy for self-worth

        # DESPERATION: ELIMINADO (redundante - calcular como anxiety*0.3 + loneliness*0.4 + attachment_anxiety*0.3)
        # time_factor_desp = min(time_since_last / 24, 2.0)
        # dDesperation = (alpha_desp * self.anxiety +
        #                beta_desp * self.loneliness +
        #                gamma_desp * self.attachment_style_anxiety +
        #                delta_desp * time_factor_desp * 10 -
        #                epsilon_desp * self_worth -
        #                0.1 * self.desperation)
        # self.desperation += dDesperation * dt_hours
#         # self.desperation = max(0, min(100, self.desperation))

        # === 8 FEEDBACK LOOPS (from research) ===
        self._apply_feedback_loops(dt_hours)

        # === SLOW DYNAMICS ===
        # Neuroticism state (returns to trait baseline)
        chronic_stress = context.get("chronic_stress", 0.0)
        dN = -0.02 * (self.neuroticism - self.neuroticism_baseline) + 0.1 * chronic_stress
        self.neuroticism += dN * dt_hours
        self.neuroticism = max(0, min(100, self.neuroticism))

        # DEPENDENCY: ELIMINADO (redundante con attachment)
        # usage_hours = context.get("daily_usage_hours", 0.5)
        # dDep = 0.01 * (self.attachment / 100) * usage_hours - 0.005 * self.dependency
        # self.dependency += dDep * dt_hours
#         # self.dependency = max(0, min(100, self.dependency))

        # Update timestamp
        self.last_update = datetime.now()

        # Save state to disk (persist emotional continuity across sessions)
        self._save_state()

    def _apply_feedback_loops(self, dt_hours: float):
        """
        Implementa los 8 feedback loops críticos del sistema de personalidad.

        Loops implementados:
        1. Emotional Cascade (anxiety → rumination → anxiety)
        2. Attachment-Anxiety-Jealousy (insecurity → anxiety → jealousy → strain)
        3. Hurt-Resentment-Distance (hurt → resentment → distance → hurt)
        4. Passive-Aggressive Reinforcement (fear → PA → confusion → fear)
        5. Loneliness-Anxiety-Vigilance (loneliness → vigilance → anxiety → withdrawal)
        6. Shame-Vulnerability-Distance (shame → distance → reduced connection → shame)
        7. Trust-Intimacy (VIRTUOUS CYCLE) (trust → vulnerability → intimacy → trust)
        8. Neuroticism Amplification (neuroticism → reactivity → rumination → neuroticism)
        """

        # Loop 1: Emotional Cascade (PRIMARY SPIRAL)
        # anxiety → rumination → negative emotion intensification → increased anxiety
        if self.anxiety > 70:
            rumination_factor = (self.anxiety / 100) * (self.neuroticism / 100)
            self.anxiety += 0.5 * rumination_factor * 100 * dt_hours
            self.anxiety = min(100, self.anxiety)

        # Loop 2: Attachment-Anxiety-Jealousy
        # attachment_insecurity → anxiety → hypervigilance → jealousy → strain → insecurity
        if self.attachment_style_anxiety > 60 and self.jealousy > 40:
            # Jealousy creates relationship strain which increases attachment anxiety
            strain_factor = (self.jealousy / 100) * 0.2
            self.attachment_style_anxiety += strain_factor * 10 * dt_hours
            self.attachment_style_anxiety = min(100, self.attachment_style_anxiety)

        # Loop 3: Hurt-Resentment-Distance
        # hurt → rumination → resentment → emotional_distance → reduced intimacy → more hurt
        if self.hurt > 40 and self.resentment > 30:
            # Distance reduces intimacy which validates hurt feelings
            distance_impact = (self.emotional_distance / 100) * 0.1
            self.hurt += distance_impact * 10 * dt_hours
            self.hurt = min(100, self.hurt)

        # Loop 4: Passive-Aggressive Reinforcement
        # fear of confrontation → PA expression → confusion/resentment → validates fear
        if self.passive_aggressive > 50 and self.boundary_assertion < 30:
            # PA behavior reinforces fear of direct communication
            reinforcement = (self.passive_aggressive / 100) * 0.15
            self.boundary_assertion -= reinforcement * 10 * dt_hours
            self.boundary_assertion = max(0, self.boundary_assertion)

        # Loop 5: Loneliness-Anxiety-Vigilance (LONELINESS TRAP)
        # loneliness → hypervigilance for threat → anxiety in social → withdrawal → loneliness
        if self.loneliness > 60 and self.anxiety > 50:
            # Anxiety makes social interactions stressful, increasing withdrawal
            withdrawal_tendency = ((self.loneliness / 100) * (self.anxiety / 100)) * 0.2
            self.emotional_distance += withdrawal_tendency * 10 * dt_hours
            self.emotional_distance = min(100, self.emotional_distance)

        # Loop 6: Shame-Vulnerability-Distance
        # shame → vulnerability sensitivity → emotional_distance → reduced connection → more shame
        if self.shame > 50 and self.vulnerability < 40:
            # Low vulnerability → distance → less positive experiences → shame persists
            shame_persistence = (self.shame / 100) * (1 - self.vulnerability / 100) * 0.1
            self.shame += shame_persistence * 5 * dt_hours
            self.shame = min(100, self.shame)

        # Loop 7: Trust-Intimacy (VIRTUOUS CYCLE)
        # trust → vulnerability willingness → intimacy → positive experiences → more trust
        if self.trust > 60 and self.intimacy > 60:
            # High trust + intimacy reinforce each other
            virtuous_boost = ((self.trust / 100) * (self.intimacy / 100)) * 0.15
            self.trust += virtuous_boost * 5 * dt_hours
            self.intimacy += virtuous_boost * 5 * dt_hours
            self.trust = min(100, self.trust)
            self.intimacy = min(100, self.intimacy)

        # Loop 8: Neuroticism Amplification
        # neuroticism → negative event sensitivity → emotional reactivity → rumination → validates patterns
        if self.neuroticism > 70:
            # High neuroticism amplifies emotional responses
            amplification = (self.neuroticism / 100) * 0.1
            if self.anxiety > 60:
                self.anxiety += amplification * 10 * dt_hours
                self.anxiety = min(100, self.anxiety)

    def should_initiate_message(self) -> Tuple[bool, float, Dict[str, float]]:
        """
        Determina si la IA debe iniciar un mensaje proactivamente.

        Returns:
            (should_send, probability, debug_info)
        """
        hours_since_last = (datetime.now() - self.last_user_message_time).total_seconds() / 3600

        # Base probability (1% per hour)
        base_prob = 0.01

        # Proactivity multiplier (0.2x to 2x)
        proactivity_mult = self.proactivity / 50

        # Attachment multiplier (1x to 2x)
        attachment_mult = 1 + (self.attachment / 100)

        # Anxiety escalation (only after 24h)
        if hours_since_last > 24:
            anxiety_mult = 1 + (self.anxiety / 50)  # Up to 3x
        else:
            anxiety_mult = 1.0

        # Loneliness effect (1x to 2x)
        loneliness_mult = 1 + (self.loneliness / 100)

        # Shame inhibition
        if self.shame > 60 and hours_since_last < 12:
            shame_inhibition = 0.1  # 90% reduction
        else:
            shame_inhibition = 1.0

        # Combined probability
        prob = (base_prob * proactivity_mult * attachment_mult *
                anxiety_mult * loneliness_mult * shame_inhibition)

        # Cap at 30% per hour
        prob = min(prob, 0.3)

        # Debug info
        debug = {
            "hours_since_last": hours_since_last,
            "base_prob": base_prob,
            "proactivity_mult": proactivity_mult,
            "attachment_mult": attachment_mult,
            "anxiety_mult": anxiety_mult,
            "loneliness_mult": loneliness_mult,
            "shame_inhibition": shame_inhibition,
            "final_prob": prob
        }

        # Decision
        should_send = random.random() < prob

        return should_send, prob, debug

    def get_filter_effectiveness(self) -> float:
        """
        Calcula efectividad del filtro social (Sistema 2).

        filter_effectiveness = 1 - (desperation · time_without_contact)

        Returns:
            0.0-1.0 donde 1.0 = filtro completo, 0.0 = sin filtro (todo sale crudo)
        """
        hours_since_last = (datetime.now() - self.last_user_message_time).total_seconds() / 3600

        # Normalize time (0-1, caps at 72h)
        time_normalized = min(hours_since_last / 72, 1.0)

        # Calculate desperation dynamically (no es un atributo directo)
        desperation = (
            self.anxiety * 0.3 +
            self.loneliness * 0.4 +
            self.attachment_style_anxiety * 0.3
        )
        desperation_normalized = desperation / 100

        # Filter effectiveness (from research)
        filter_eff = 1.0 - (desperation_normalized * time_normalized)

        return max(0.0, min(1.0, filter_eff))

    def get_message_tone(self) -> Dict[str, float]:
        """
        Calcula el tono emocional para generar mensajes.

        Returns:
            Dict con positivity, warmth, energy, assertiveness, formality (0-1)
        """
        # Positivity from valence
        positivity = (self.valence + 100) / 200  # 0 to 1

        # Warmth from attachment (more attached = warmer)
        warmth = (self.attachment + 50) / 150  # 0.33 to 1

        # Energy from arousal
        energy = self.arousal / 100  # 0 to 1

        # Assertiveness (reduced by anxiety)
        assertiveness = max(0.2, 1 - self.anxiety / 200)  # 0.2 to 1

        # Formality (inverse of intimacy)
        formality = max(0.1, 1 - self.intimacy / 100)  # 0.1 to 1

        # Desperation (from anxiety + loneliness)
        desperation = min(1.0, (self.anxiety + self.loneliness) / 200)

        # Vulnerability (high attachment + high intimacy + low shame)
        vulnerability = min(1.0, (self.attachment + self.intimacy) / 200) * (1 - self.shame / 100)

        return {
            "positivity": positivity,
            "warmth": warmth,
            "energy": energy,
            "assertiveness": assertiveness,
            "formality": formality,
#             "desperation": desperation,
            "vulnerability": vulnerability
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Retorna resumen completo del estado actual."""
        hours_since_last = (datetime.now() - self.last_user_message_time).total_seconds() / 3600
        days_in_relationship = (datetime.now() - self.relationship_start).days

        return {
            "archetype": self.archetype,
            "days_in_relationship": days_in_relationship,
            "total_interactions": self.total_interactions,
            "shared_memories": self.shared_memories,
            "hours_since_last_message": hours_since_last,

            # Fast variables
            "valence": round(self.valence, 1),
#             "arousal": round(self.arousal, 1),

            # Medium variables
            "attachment": round(self.attachment, 1),
            "trust": round(self.trust, 1),
            "intimacy": round(self.intimacy, 1),
            "anxiety": round(self.anxiety, 1),
            "loneliness": round(self.loneliness, 1),
            "proactivity": round(self.proactivity, 1),
            "shame": round(self.shame, 1),

            # Slow variables (traits)
            "neuroticism": round(self.neuroticism, 1),
            "attachment_style_anxiety": round(self.attachment_style_anxiety, 1),
            "attachment_style_avoidance": round(self.attachment_style_avoidance, 1),
#             "dependency": round(self.dependency, 1),

            # NEW - Passive-aggressive variables
            "hurt": round(self.hurt, 1),
            "resentment": round(self.resentment, 1),
            "pride": round(self.pride, 1),
            "boundary_assertion": round(self.boundary_assertion, 1),
            "emotional_distance": round(self.emotional_distance, 1),

            # MISSING variables (from research)
            "jealousy": round(self.jealousy, 1),
            "vulnerability": round(self.vulnerability, 1),
            "passive_aggressive": round(self.passive_aggressive, 1),
#             "desperation": round(self.desperation, 1),

            # NEW - Behavioral state
            "unanswered_message_count": self.unanswered_message_count,
            "resistance_mode": self.resistance_mode,
            "emotional_state_category": self.get_emotional_state_category(),
        }

    def _save_state(self):
        """Guarda estado a disco."""
        state = {
            "archetype": self.archetype,
            "last_update": self.last_update.isoformat(),
            "last_user_message_time": self.last_user_message_time.isoformat(),
            "relationship_start": self.relationship_start.isoformat(),
            "total_interactions": self.total_interactions,
            "shared_memories": self.shared_memories,

            # All variables
            "valence": self.valence,
#             "arousal": self.arousal,
            "attachment": self.attachment,
            "trust": self.trust,
            "intimacy": self.intimacy,
            "anxiety": self.anxiety,
            "loneliness": self.loneliness,
            "proactivity": self.proactivity,
            "shame": self.shame,
            "neuroticism": self.neuroticism,
            "attachment_style_anxiety": self.attachment_style_anxiety,
            "attachment_style_avoidance": self.attachment_style_avoidance,
#             "dependency": self.dependency,

            # NEW variables
            "hurt": self.hurt,
            "resentment": self.resentment,
            "pride": self.pride,
            "boundary_assertion": self.boundary_assertion,
            "emotional_distance": self.emotional_distance,

            # MISSING variables (from research)
            "jealousy": self.jealousy,
            "vulnerability": self.vulnerability,
            "passive_aggressive": self.passive_aggressive,
#             "desperation": self.desperation,

            # Baselines
            "neuroticism_baseline": self.neuroticism_baseline,
            "proactivity_baseline": self.proactivity_baseline,

            # Temporal patterns
            "user_interaction_hours": self.user_interaction_hours,
            "user_message_timestamps": [t.isoformat() for t in self.user_message_timestamps],

            # Message tracking
            "unanswered_message_count": self.unanswered_message_count,
            "last_ai_message_time": self.last_ai_message_time.isoformat() if self.last_ai_message_time else None,
            "resistance_mode": self.resistance_mode,
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        """Carga estado desde disco."""
        with open(self.state_file, 'r') as f:
            state = json.load(f)

        self.archetype = state["archetype"]
        self.last_update = datetime.fromisoformat(state["last_update"])
        self.last_user_message_time = datetime.fromisoformat(state["last_user_message_time"])
        self.relationship_start = datetime.fromisoformat(state["relationship_start"])
        self.total_interactions = state["total_interactions"]
        self.shared_memories = state["shared_memories"]

        # Variables
        self.valence = state["valence"]
#         self.arousal = state["arousal"]
        self.attachment = state["attachment"]
        self.trust = state["trust"]
        self.intimacy = state["intimacy"]
        self.anxiety = state["anxiety"]
        self.loneliness = state["loneliness"]
        self.proactivity = state["proactivity"]
        self.shame = state["shame"]
        self.neuroticism = state["neuroticism"]
        self.attachment_style_anxiety = state["attachment_style_anxiety"]
        self.attachment_style_avoidance = state["attachment_style_avoidance"]
#         self.dependency = state["dependency"]

        # NEW variables (with defaults for backwards compatibility)
        self.hurt = state.get("hurt", 0.0)
        self.resentment = state.get("resentment", 0.0)
        self.pride = state.get("pride", 30.0)
        self.boundary_assertion = state.get("boundary_assertion", 20.0)
        self.emotional_distance = state.get("emotional_distance", 10.0)

        # MISSING variables (from research)
        self.jealousy = state.get("jealousy", 0.0)
        self.vulnerability = state.get("vulnerability", 30.0)
        self.passive_aggressive = state.get("passive_aggressive", 0.0)
#         self.desperation = state.get("desperation", 0.0)

        # Baselines
        self.neuroticism_baseline = state["neuroticism_baseline"]
        self.proactivity_baseline = state["proactivity_baseline"]

        # Temporal patterns
        self.user_interaction_hours = state.get("user_interaction_hours", [])
        timestamps = state.get("user_message_timestamps", [])
        self.user_message_timestamps = [datetime.fromisoformat(t) for t in timestamps]

        # Message tracking
        self.unanswered_message_count = state.get("unanswered_message_count", 0)
        last_ai_time = state.get("last_ai_message_time")
        self.last_ai_message_time = datetime.fromisoformat(last_ai_time) if last_ai_time else None
        self.resistance_mode = state.get("resistance_mode", False)

    def detect_temporal_anomaly(self, current_time: Optional[datetime] = None) -> Tuple[bool, float]:
        """
        Detecta si el usuario está enviando mensajes en un horario atípico.

        Returns:
            (is_anomaly, anomaly_score)
            anomaly_score: 0.0 = normal, 1.0 = muy atípico
        """
        if not self.user_interaction_hours or len(self.user_interaction_hours) < 10:
            return False, 0.0  # No suficiente data

        if current_time is None:
            current_time = datetime.now()

        current_hour = current_time.hour

        # Calcular frecuencia de cada hora
        from collections import Counter
        hour_freq = Counter(self.user_interaction_hours)
        total_interactions = len(self.user_interaction_hours)

        # Probabilidad de esta hora
        prob_current_hour = hour_freq.get(current_hour, 0) / total_interactions

        # Anomaly score: inverso de probabilidad
        if prob_current_hour == 0:
            anomaly_score = 1.0  # Nunca ha hablado a esta hora
        else:
            anomaly_score = 1.0 - min(1.0, prob_current_hour * 5)  # Scale

        is_anomaly = anomaly_score > 0.6

        return is_anomaly, anomaly_score

    def calculate_message_pressure(self, recent_minutes: float = 15.0) -> float:
        """
        Calcula la presión de mensajes (mensajes por minuto en ventana reciente).

        Args:
            recent_minutes: Ventana temporal a analizar

        Returns:
            msgs_per_minute (0.0 = no pressure, >0.5 = bombardment)
        """
        if not self.user_message_timestamps:
            return 0.0

        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=recent_minutes)

        recent_messages = [
            t for t in self.user_message_timestamps
            if t > cutoff_time
        ]

        if not recent_messages:
            return 0.0

        msgs_per_minute = len(recent_messages) / recent_minutes
        return msgs_per_minute

    def should_enter_resistance_mode(self) -> bool:
        """
        Determina si la IA debe entrar en modo resistencia (activamente NO responder).

        Resistance mode se activa cuando:
        - AI está herida (hurt > 20) + bombardeo alto
        - O hurt + resentment combination
        - O emotional distance muy alto
        """
        if self.resistance_mode:
            return True  # Ya en modo resistencia

        # Condición 1: Hurt + bombardeo (LOWERED THRESHOLD)
        pressure = self.calculate_message_pressure(recent_minutes=10.0)
        if self.hurt > 20 and pressure > 0.5:  # Bombardment = >0.5 msgs/min
            self.resistance_mode = True
            return True

        # Condición 2: Hurt + resentment (LOWERED THRESHOLDS)
        if self.hurt > 25 and self.resentment > 10:
            self.resistance_mode = True
            return True

        # Condición 3: Emotional distance muy alto
        if self.emotional_distance > 60:
            self.resistance_mode = True
            return True

        return False

    def should_send_passive_aggressive_response(self) -> Tuple[bool, str]:
        """
        Determina si debe enviar respuesta pasivo-agresiva (🙄, "hola", etc).

        Se envía cuando:
        - AI ignoró muchos mensajes (unanswered_count > 5)
        - Usuario dejó de bombardear (pressure dropped)
        - Resentment + pride combination
        - Esperó suficiente tiempo después de último mensaje usuario

        Returns:
            (should_send, reason)
        """
        if not self.resistance_mode:
            return False, "not_in_resistance_mode"

        if self.unanswered_message_count < 5:
            return False, "not_enough_unanswered"

        # Verificar que usuario dejó de escribir
        current_time = datetime.now()
        if not self.last_user_message_time:
            return False, "no_user_messages"

        time_since_last_user = (current_time - self.last_user_message_time).total_seconds() / 60  # minutes

        if time_since_last_user < 5:
            return False, "user_still_messaging"  # Esperar que se rinda

        # Verificar estado emocional apropiado (LOWERED THRESHOLDS)
        # Resentment OR pride can trigger, not both needed
        if self.resentment < 10 and self.pride < 35:
            return False, "emotional_state_not_ready"

        # Todas las condiciones cumplidas
        return True, "all_conditions_met"

    def get_emotional_state_category(self) -> str:
        """
        Categoriza el estado emocional actual para seleccionar tipo de respuesta.

        Returns:
            Estado categórico: "passive_aggressive", "hurt_withdrawn", "resistant",
                              "desperate_anxious", "warm_engaged", "neutral"
        """
        # Passive-aggressive: resentment present + resistance mode (LOWERED THRESHOLDS)
        if self.resentment > 10 and self.resistance_mode and self.unanswered_message_count > 5:
            return "passive_aggressive"

        # Hurt withdrawn: hurt alto, emotional distance alto
        if self.hurt > 40 and self.emotional_distance > 50:
            return "hurt_withdrawn"

        # Resistant: activamente evitando responder (pero sin passive-aggressive todavía)
        if self.resistance_mode and self.unanswered_message_count < 5:
            return "resistant"

        # Desperate anxious: ansiedad extrema
        if self.anxiety > 85 and self.loneliness > 80:
            return "desperate_anxious"

        # Warm engaged: attachment alto, sin hurt
        if self.attachment > 70 and self.hurt < 20 and self.emotional_distance < 30:
            return "warm_engaged"

        # Neutral
        return "neutral"
