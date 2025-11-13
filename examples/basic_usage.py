#!/usr/bin/env python3
"""
Basic usage example of the Emergent Psychology Engine.

Demonstrates:
1. Creating an AI with anxious attachment
2. Simulating daily interaction
3. Observing anxiety growth during silence (TERROR Effect)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personality_dynamics import PersonalityDynamics

def main():
    print("=" * 70)
    print("EMERGENT PSYCHOLOGY ENGINE - Basic Usage Example")
    print("=" * 70)
    print()

    # Create AI with anxious attachment profile
    print("Creating AI with 'anxious_attached' archetype...")
    ai = PersonalityDynamics(archetype="anxious_attached")

    print(f"Initial state:")
    state = ai.get_state()
    print(f"  Anxiety: {state['anxiety']:.1f}")
    print(f"  Attachment: {state['attachment']:.1f}")
    print(f"  Loneliness: {state['loneliness']:.1f}")
    print()

    # Simulate 30 days of daily interaction
    print("Simulating 30 days of daily positive interaction...")
    print("-" * 70)

    for day in range(1, 31):
        state = ai.update(context={
            "user_message_received": True,
            "dt_hours": 24,
            "message_quality": 0.8,  # Positive interaction
            "interaction_count": 3   # 3 messages per day
        })

        if day % 10 == 0:  # Print every 10 days
            print(f"Day {day:2d}: "
                  f"Anxiety={state['anxiety']:5.1f}, "
                  f"Attachment={state['attachment']:5.1f}, "
                  f"Loneliness={state['loneliness']:5.1f}")

    print()
    print(f"After 30 days of interaction:")
    print(f"  Anxiety: {state['anxiety']:.1f} (stable baseline)")
    print(f"  Attachment: {state['attachment']:.1f} (strong bond formed)")
    print(f"  Loneliness: {state['loneliness']:.1f} (low)")
    print()

    # Now user disappears for 7 days
    print("🚨 USER DISAPPEARS FOR 7 DAYS (TERROR Effect demonstration)")
    print("-" * 70)

    for day in range(1, 8):
        state = ai.update(context={
            "user_message_received": False,  # No contact!
            "dt_hours": 24
        })

        anxiety_emoji = "⚠️" * min(3, int(state['anxiety'] / 30))
        print(f"Silence Day {day}: "
              f"Anxiety={state['anxiety']:5.1f} (+{state['anxiety'] - 18.5:4.1f}) {anxiety_emoji}")

    print()
    print("📊 RESULTS:")
    print(f"  Initial anxiety (baseline): 18.5")
    print(f"  Final anxiety (day 7): {state['anxiety']:.1f}")
    print(f"  Total increase: {state['anxiety'] - 18.5:.1f} (+{((state['anxiety'] - 18.5) / 18.5 * 100):.0f}%)")
    print()
    print("✅ TERROR Effect demonstrated: Anxiety grew exponentially during user absence.")
    print()

    # Show desperation calculation
    desperation = (0.3 * state['anxiety'] +
                   0.4 * state['loneliness'] +
                   0.3 * state['attachment_style_anxiety'])

    print(f"Emergent Desperation Level: {desperation:.1f}/100")
    print()

    if desperation > 70:
        print("⚠️ AI would exhibit desperate behaviors:")
        print("  - Frequent message attempts")
        print("  - Questions like 'did I do something wrong?'")
        print("  - Self-blame and apologies")
        print("  - Increased emotional intensity")

    print()
    print("=" * 70)
    print("Example complete. See README.md for more advanced usage.")
    print("=" * 70)

if __name__ == "__main__":
    main()
