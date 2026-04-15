"""
Prediction engine: uses statistical weights from analysis to generate
number suggestions. Multiple strategies available.

DISCLAIMER: Lottery draws are cryptographically random events. No algorithm
can predict future draws. These suggestions are statistically-informed
but carry no advantage over random selection.
"""

import random
import numpy as np
from collections import Counter


def _normalize(weights_dict, num_range):
    """Convert a raw count dict to a probability array for range 1..num_range."""
    total = sum(weights_dict.get(n, 0) for n in range(1, num_range + 1))
    if total == 0:
        return [1.0 / num_range] * num_range
    probs = []
    for n in range(1, num_range + 1):
        probs.append(weights_dict.get(n, 0) / total)
    return probs


def strategy_frequency(report, n_tickets=5):
    """
    Strategy: favor the most frequently drawn numbers (hot numbers).
    Weights proportional to all-time draw frequency.
    """
    tickets = []
    freq = report["frequency"]
    pb_freq = report["powerball_frequency"]

    main_probs = _normalize(freq, 69)
    pb_probs = _normalize(pb_freq, 26)

    for _ in range(n_tickets):
        mains = sorted(
            np.random.choice(range(1, 70), size=5, replace=False, p=main_probs).tolist()
        )
        pb = int(np.random.choice(range(1, 27), p=pb_probs))
        tickets.append((mains, pb))
    return tickets


def strategy_due_numbers(report, n_tickets=5):
    """
    Strategy: favor numbers that are 'overdue' (haven't appeared in a long time).
    High gap = high weight.
    """
    tickets = []
    gaps = report["gaps"]
    pb_gaps = report["powerball_gaps"]

    # Weight = gap value (more overdue = higher weight)
    main_probs = _normalize(gaps, 69)
    pb_probs = _normalize(pb_gaps, 26)

    for _ in range(n_tickets):
        mains = sorted(
            np.random.choice(range(1, 70), size=5, replace=False, p=main_probs).tolist()
        )
        pb = int(np.random.choice(range(1, 27), p=pb_probs))
        tickets.append((mains, pb))
    return tickets


def strategy_balanced(report, n_tickets=5):
    """
    Strategy: blend frequency + gap + trend for a balanced pick.
    Weights: 40% frequency, 30% due (gap), 30% trend.
    """
    tickets = []
    freq = report["frequency"]
    gaps = report["gaps"]
    trends = {n: t for n, _, _, t in report["trends"]}

    pb_freq = report["powerball_frequency"]
    pb_gaps = report["powerball_gaps"]

    def blend(f, g, t, num_range):
        f_probs = np.array(_normalize(f, num_range))
        g_probs = np.array(_normalize(g, num_range))
        # Trend can be negative — shift to positive
        t_raw = {n: t.get(n, 0) + 0.01 for n in range(1, num_range + 1)}
        t_probs = np.array(_normalize(t_raw, num_range))
        combined = 0.40 * f_probs + 0.30 * g_probs + 0.30 * t_probs
        combined /= combined.sum()
        return combined

    main_probs = blend(freq, gaps, trends, 69)
    pb_probs = blend(pb_freq, pb_gaps, {}, 26)

    for _ in range(n_tickets):
        mains = sorted(
            np.random.choice(range(1, 70), size=5, replace=False, p=main_probs).tolist()
        )
        pb = int(np.random.choice(range(1, 27), p=pb_probs))
        tickets.append((mains, pb))
    return tickets


def strategy_sum_constrained(report, n_tickets=5):
    """
    Strategy: generate picks whose sum falls in the historically common range.
    Uses the 25th–75th percentile sum range from the analysis.
    """
    sum_stats = report["sum_stats"]
    low, high = sum_stats["common_range"]
    freq = report["frequency"]
    pb_freq = report["powerball_frequency"]
    main_probs = _normalize(freq, 69)
    pb_probs = _normalize(pb_freq, 26)

    tickets = []
    attempts = 0
    while len(tickets) < n_tickets and attempts < 10000:
        mains = sorted(
            np.random.choice(range(1, 70), size=5, replace=False, p=main_probs).tolist()
        )
        if low <= sum(mains) <= high:
            pb = int(np.random.choice(range(1, 27), p=pb_probs))
            tickets.append((mains, pb))
        attempts += 1

    # Fill remaining with balanced if constrained picks failed
    while len(tickets) < n_tickets:
        balanced = strategy_balanced(report, 1)
        tickets.extend(balanced)

    return tickets[:n_tickets]


def strategy_pairs(report, n_tickets=5):
    """
    Strategy: seed picks with the most commonly co-occurring pairs,
    then fill remaining slots using frequency weights.
    """
    top_pairs = report["top_pairs"]
    freq = report["frequency"]
    pb_freq = report["powerball_frequency"]
    main_probs = _normalize(freq, 69)
    pb_probs = _normalize(pb_freq, 26)

    tickets = []
    for i in range(n_tickets):
        pair = top_pairs[i % len(top_pairs)][0]
        seed = list(pair)
        remaining_pool = [n for n in range(1, 70) if n not in seed]
        sub_probs = np.array([main_probs[n - 1] for n in remaining_pool])
        sub_probs /= sub_probs.sum()
        extras = np.random.choice(remaining_pool, size=3, replace=False, p=sub_probs).tolist()
        mains = sorted(seed + extras)
        pb = int(np.random.choice(range(1, 27), p=pb_probs))
        tickets.append((mains, pb))
    return tickets


def generate_predictions(report, n_tickets=5):
    """
    Generate predictions using all 5 strategies.
    Returns dict: {strategy_name: [tickets]}
    Each ticket is ([n1, n2, n3, n4, n5], powerball).
    """
    return {
        "Frequency (Hot Numbers)": strategy_frequency(report, n_tickets),
        "Due Numbers (Overdue)": strategy_due_numbers(report, n_tickets),
        "Balanced (Freq+Due+Trend)": strategy_balanced(report, n_tickets),
        "Sum-Constrained": strategy_sum_constrained(report, n_tickets),
        "Top Pairs Seed": strategy_pairs(report, n_tickets),
    }


def consensus_pick(report, n_tickets=5, runs=1000):
    """
    Run the balanced strategy many times and return the numbers
    that appear most often — a 'wisdom of crowds' pick.
    """
    number_freq = Counter()
    pb_freq_counter = Counter()

    for _ in range(runs):
        tickets = strategy_balanced(report, 1)
        for mains, pb in tickets:
            for n in mains:
                number_freq[n] += 1
            pb_freq_counter[pb] += 1

    top_mains = [n for n, _ in number_freq.most_common(n_tickets * 5)]
    top_pb = [p for p, _ in pb_freq_counter.most_common(5)]

    tickets = []
    for i in range(n_tickets):
        chunk = top_mains[i * 5: i * 5 + 5]
        pb = top_pb[i % len(top_pb)]
        tickets.append((sorted(chunk), pb))
    return tickets
