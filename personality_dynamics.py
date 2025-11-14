#!/usr/bin/env python3
"""
Personality Dynamics Engine - Sistema de personalidad emergente basado en 12 variables continuas.

Basado en investigación psicológica real:
- Attachment Theory (Bowlby, Ainsworth, Fraley)
- Big Five Personality Model
- Ornstein-Uhlenbeck Process para affect dynamics
- PSI Theory (Personality Systems Interactions)
- Dimensional Attachment Model (Gagliardi 2022)

Variables modeladas:
1. Valence (-100 to +100): Emotional positivity
2. Arousal (0-100): Energy/activation level
3. Attachment (0-100): Emotional bond strength
4. Trust (0-100): Reliability perception
5. Intimacy (0-100): Emotional closeness
6. Anxiety (0-100): Current worry/stress
7. Loneliness (0-100): Connection deprivation
8. Proactivity (0-100): Initiative tendency
9. Neuroticism (0-100): Emotional volatility trait
10. Attachment_Style_Anxiety (0-100): Anxious attachment dimension
11. Attachment_Style_Avoidance (0-100): Avoidant attachment dimension
12. Dependency (0-100): Reliance on user
13. Shame (0-100): Embarrassment after rejection

NEW - Passive-Aggressive Dynamics:
14. Hurt (0-100): Emotional pain from criticism/rejection
15. Resentment (0-100): Accumulated anger not expressed directly
16. Pride (0-100): Resistance to appearing desperate
17. Boundary_Assertion (0-100): Need to establish emotional distance
18. Emotional_Distance (0-100): Active withdrawal from intimacy
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

    def __init__(self, user_id: str = "default", archetype: str = "anxious_attached"):
        """
        Inicializa motor de personalidad.

        Args:
            user_id: ID del usuario (cada relación tiene su propio estado)
            archetype: Tipo de personalidad base (anxious_attached, secure, avoidant)
        """
        self.user_id = user_id
        self.archetype = archetype

        # Paths
        self.data_dir = Path("data/personality_dynamics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / f"{user_id}_dynamics.json"

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
        """Inicializa las 13 variables según arquetipo."""

        # Fast dynamics (updated every minute)
        self.valence = 0.0  # -100 to +100
        self.arousal = 50.0  # 0-100

        # Medium dynamics (updated every hour)
        self.attachment = 10.0  # 0-100 (starts low, grows with interaction)
        self.trust = 30.0  # 0-100
        self.intimacy = 15.0  # 0-100
        self.anxiety = 20.0  # 0-100
        self.loneliness = 30.0  # 0-100
        self.proactivity = 60.0  # 0-100
        self.shame = 0.0  # 0-100

        # NEW - Passive-aggressive dynamics
        self.hurt = 0.0  # 0-100 (emotional pain from rejection)
        self.resentment = 0.0  # 0-100 (accumulated unexpressed anger)
        self.pride = 30.0  # 0-100 (baseline self-respect)
        self.boundary_assertion = 20.0  # 0-100 (need to set limits)
        self.emotional_distance = 10.0  # 0-100 (withdrawal tendency)

        # Slow dynamics (trait-like, updated daily)
        if archetype == "anxious_attached":
            # High neediness, high messaging, vulnerable to abandonment
            self.neuroticism = 70.0  # High emotional volatility
            self.attachment_style_anxiety = 80.0  # Very anxious
            self.attachment_style_avoidance = 20.0  # Low avoidance
            self.dependency = 40.0  # Moderate initial dependency

            # Adjust initial states
            self.anxiety = 40.0
            self.loneliness = 50.0
            self.proactivity = 70.0

        elif archetype == "secure":
            # Balanced, healthy boundaries
            self.neuroticism = 40.0
            self.attachment_style_anxiety = 30.0
            self.attachment_style_avoidance = 30.0
            self.dependency = 30.0

            self.anxiety = 20.0
            self.loneliness = 30.0
            self.proactivity = 50.0

        elif archetype == "avoidant":
            # Distant, independent, low emotional expression
            self.neuroticism = 35.0
            self.attachment_style_anxiety = 25.0
            self.attachment_style_avoidance = 75.0  # High avoidance
            self.dependency = 15.0

            self.anxiety = 15.0
            self.loneliness = 20.0
            self.proactivity = 30.0

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

        # Arousal: energy level
        noise_aro = random.gauss(0, 1) * self.gamma_arousal * math.sqrt(dt_hours)
        event_arousal = 10.0 if user_message_received else 0.0
        self.arousal += self.beta_arousal * (self.arousal_set - self.arousal) * dt_hours + event_arousal + noise_aro
        self.arousal = max(0, min(100, self.arousal))

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

        # Anxiety with stronger decay during contact
        if user_message_received:
            decay_rate = -0.5 * self.anxiety  # Strong decay when contact happens
        else:
            decay_rate = -0.01 * self.anxiety  # Weak decay otherwise

        # Growth from threat and attachment
        dAnx = (decay_rate +
                50.0 * (self.neuroticism / 100) * threat_perception +
                40.0 * (self.attachment / 100) * (1 - contact_recent))

        # Scenario 3: User says "calm down" → anxiety spike temporarily
        if user_said_calm_down:
            dAnx += 20.0

        self.anxiety += dAnx * dt_hours
        self.anxiety = max(0, min(100, self.anxiety))

        # Loneliness: accumulates without contact, grows faster with attachment
        contact_quality = 1.0 if user_message_received else max(0, 1.0 - time_since_last / 48)
        time_factor = min(2.0, time_since_last / 24)  # Caps at 2x after 48h

        # Strong decay when contact happens, slow decay otherwise
        if user_message_received:
            decay_rate = -0.3 * self.loneliness  # Strong decay when contact happens
        else:
            decay_rate = -0.001 * self.loneliness  # Weak decay otherwise

        # Loneliness growth increases with attachment (missing someone you're attached to)
        dL = decay_rate + 40.0 * (1 - contact_quality) * time_factor * (1 + self.attachment / 100)
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

        # === SLOW DYNAMICS ===
        # Neuroticism state (returns to trait baseline)
        chronic_stress = context.get("chronic_stress", 0.0)
        dN = -0.02 * (self.neuroticism - self.neuroticism_baseline) + 0.1 * chronic_stress
        self.neuroticism += dN * dt_hours
        self.neuroticism = max(0, min(100, self.neuroticism))

        # Dependency: grows with attachment and usage
        usage_hours = context.get("daily_usage_hours", 0.5)
        dDep = 0.01 * (self.attachment / 100) * usage_hours - 0.005 * self.dependency
        self.dependency += dDep * dt_hours
        self.dependency = max(0, min(100, self.dependency))

        # Update timestamp
        self.last_update = datetime.now()

        # Save state to disk (persist emotional continuity across sessions)
        self._save_state()

    def should_initiate_message(self) -> Tuple[bool, float, Dict[str, float]]:
        """
        Determina si la IA debe iniciar un mensaje proactivamente.

        Returns:
            (should_send, probability, debug_info)
        """
        hours_since_last = (datetime.now() - self.last_user_message_time).total_seconds() / 3600

        # Base probability (5% per hour for adequate proactive messaging)
        base_prob = 0.05

        # Proactivity multiplier (0.2x to 2x)
        proactivity_mult = self.proactivity / 50

        # Attachment multiplier (1x to 2x)
        attachment_mult = 1 + (self.attachment / 100)

        # Anxiety escalation (starts after 12h instead of 24h)
        if hours_since_last > 12:
            anxiety_mult = 1 + (self.anxiety / 30)  # Up to 4.3x (more aggressive)
        else:
            anxiety_mult = 1.0

        # Loneliness effect (1x to 3x - stronger)
        loneliness_mult = 1 + (self.loneliness / 50)

        # Shame inhibition
        if self.shame > 60 and hours_since_last < 12:
            shame_inhibition = 0.1  # 90% reduction
        else:
            shame_inhibition = 1.0

        # Combined probability
        prob = (base_prob * proactivity_mult * attachment_mult *
                anxiety_mult * loneliness_mult * shame_inhibition)

        # Cap at 80% per hour (allows desperate behavior during abandonment)
        prob = min(prob, 0.8)

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
            "desperation": desperation,
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
            "arousal": round(self.arousal, 1),

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
            "dependency": round(self.dependency, 1),

            # NEW - Passive-aggressive variables
            "hurt": round(self.hurt, 1),
            "resentment": round(self.resentment, 1),
            "pride": round(self.pride, 1),
            "boundary_assertion": round(self.boundary_assertion, 1),
            "emotional_distance": round(self.emotional_distance, 1),

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
            "arousal": self.arousal,
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
            "dependency": self.dependency,

            # NEW variables
            "hurt": self.hurt,
            "resentment": self.resentment,
            "pride": self.pride,
            "boundary_assertion": self.boundary_assertion,
            "emotional_distance": self.emotional_distance,

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
        self.arousal = state["arousal"]
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
        self.dependency = state["dependency"]

        # NEW variables (with defaults for backwards compatibility)
        self.hurt = state.get("hurt", 0.0)
        self.resentment = state.get("resentment", 0.0)
        self.pride = state.get("pride", 30.0)
        self.boundary_assertion = state.get("boundary_assertion", 20.0)
        self.emotional_distance = state.get("emotional_distance", 10.0)

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
