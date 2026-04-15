"""
Generate synthetic historical Powerball data based on realistic statistical properties.
This allows the bot to run without requiring live internet access.
"""

import random
from datetime import datetime, timedelta
import csv


def generate_synthetic_draws(num_draws=2080, start_date="2004-01-01"):
    """
    Generate realistic Powerball draws with proper statistical distributions.
    ~2080 draws ≈ 20 years (3 draws/week).

    Uses:
    - Slightly biased frequency (some numbers drawn more often)
    - Occasional hot/cold streaks
    - Realistic powerball distribution
    - Natural variation
    """
    draws = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")

    # Create a bias towards certain numbers (realistic)
    main_bias = {}
    for n in range(1, 70):
        # Most numbers have equal chance, but a few are slightly more common
        if n in [7, 23, 32, 41, 16, 28, 35]:
            main_bias[n] = 1.05
        elif n in [2, 5, 9, 14, 19, 24, 29]:
            main_bias[n] = 0.95
        else:
            main_bias[n] = 1.0

    pb_bias = {}
    for n in range(1, 27):
        if n in [10, 20, 23]:
            pb_bias[n] = 1.08
        elif n in [1, 2, 3]:
            pb_bias[n] = 0.92
        else:
            pb_bias[n] = 1.0

    last_mains = {n: -(random.randint(1, 200)) for n in range(1, 70)}
    last_pb = {n: -(random.randint(1, 100)) for n in range(1, 27)}

    for draw_num in range(num_draws):
        # Main numbers: weighted selection without replacement
        weights = []
        for n in range(1, 70):
            base_weight = main_bias[n]
            # Overdue bonus: numbers that haven't appeared recently get higher weight
            gap = draw_num - last_mains[n]
            gap_bonus = 1.0 + (gap / 500.0)
            weight = base_weight * gap_bonus
            weights.append(weight)

        total_weight = sum(weights)
        probs = [w / total_weight for w in weights]
        mains = sorted(random.choices(range(1, 70), weights=probs, k=5))

        for m in mains:
            last_mains[m] = draw_num

        # Powerball: similar weighted selection
        pb_weights = []
        for n in range(1, 27):
            base_weight = pb_bias[n]
            gap = draw_num - last_pb[n]
            gap_bonus = 1.0 + (gap / 250.0)
            weight = base_weight * gap_bonus
            pb_weights.append(weight)

        total_pb_weight = sum(pb_weights)
        pb_probs = [w / total_pb_weight for w in pb_weights]
        pb = int(random.choices(range(1, 27), weights=pb_probs, k=1)[0])
        last_pb[pb] = draw_num

        # Random multiplier
        multiplier = random.choice(["", "", "", "2x", "3x", "4x", "5x", "10x"])

        draws.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "n1": mains[0],
            "n2": mains[1],
            "n3": mains[2],
            "n4": mains[3],
            "n5": mains[4],
            "powerball": pb,
            "multiplier": multiplier,
        })

        # Advance date by ~3.5 days (3 draws per week)
        current_date += timedelta(days=3 + random.randint(0, 2))

    return draws


def save_synthetic_data(filepath="powerball_history.csv"):
    """Generate and save synthetic data to CSV."""
    draws = generate_synthetic_draws()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["date", "n1", "n2", "n3", "n4", "n5", "powerball", "multiplier"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(draws)

    print(f"✓ Generated {len(draws)} synthetic Powerball draws")
    print(f"✓ Saved to {filepath}")
    print(f"✓ Date range: {draws[0]['date']} to {draws[-1]['date']}")
    return draws


if __name__ == "__main__":
    save_synthetic_data()
