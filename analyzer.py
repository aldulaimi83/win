"""
Statistical analysis engine for Powerball historical data.
Computes frequency, gaps, pairs, positional tendencies, and trend windows.
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def build_dataframe(draws):
    """Convert raw draw dicts into a pandas DataFrame."""
    df = pd.DataFrame(draws)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def main_ball_range(df):
    """Determine the main ball range (changed from 1-59 to 1-69 in Oct 2015)."""
    # Pre-Oct 2015: 1–59; Post: 1–69
    return 59, 69


def frequency_analysis(df):
    """
    Count how often each number (1–69) appears across all draws.
    Returns a dict: {number: count}
    """
    all_mains = []
    for col in ["n1", "n2", "n3", "n4", "n5"]:
        all_mains.extend(df[col].tolist())
    freq = Counter(all_mains)
    return dict(sorted(freq.items()))


def powerball_frequency(df):
    """Count frequency of each Powerball number (1–26)."""
    return dict(Counter(df["powerball"].tolist()))


def gap_analysis(df):
    """
    For each number, calculate how many draws have passed since it last appeared.
    Returns dict: {number: draws_since_last_seen}
    """
    last_seen = {}
    total_draws = len(df)
    for idx, row in df.iterrows():
        for col in ["n1", "n2", "n3", "n4", "n5"]:
            last_seen[row[col]] = idx

    gaps = {}
    for num in range(1, 70):
        if num in last_seen:
            gaps[num] = (total_draws - 1) - last_seen[num]
        else:
            gaps[num] = total_draws
    return gaps


def powerball_gap_analysis(df):
    """Gap analysis for Powerball numbers."""
    last_seen = {}
    total_draws = len(df)
    for idx, row in df.iterrows():
        last_seen[row["powerball"]] = idx

    gaps = {}
    for num in range(1, 27):
        if num in last_seen:
            gaps[num] = (total_draws - 1) - last_seen[num]
        else:
            gaps[num] = total_draws
    return gaps


def hot_cold_numbers(df, window=50):
    """
    Hot = appeared most in last `window` draws.
    Cold = appeared least in last `window` draws.
    Returns (hot_list, cold_list) sorted by frequency desc/asc.
    """
    recent = df.tail(window)
    recent_nums = []
    for col in ["n1", "n2", "n3", "n4", "n5"]:
        recent_nums.extend(recent[col].tolist())

    freq = Counter(recent_nums)
    # Fill in zeros for numbers that didn't appear
    for n in range(1, 70):
        freq.setdefault(n, 0)

    hot = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    cold = sorted(freq.items(), key=lambda x: x[1])
    return hot[:20], cold[:20]


def powerball_hot_cold(df, window=50):
    """Hot/cold for Powerball number."""
    recent = df.tail(window)
    freq = Counter(recent["powerball"].tolist())
    for n in range(1, 27):
        freq.setdefault(n, 0)
    hot = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    cold = sorted(freq.items(), key=lambda x: x[1])
    return hot[:10], cold[:10]


def pair_analysis(df, top_n=20):
    """
    Find which pairs of numbers appear together most often.
    Returns list of ((n1, n2), count) sorted desc.
    """
    pair_counts = Counter()
    for _, row in df.iterrows():
        nums = sorted([row["n1"], row["n2"], row["n3"], row["n4"], row["n5"]])
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                pair_counts[(nums[i], nums[j])] += 1
    return pair_counts.most_common(top_n)


def positional_analysis(df):
    """
    For each position (1–5), find the most frequent numbers drawn in that position.
    Note: draws are sorted ascending, so position reflects sorted order.
    Returns dict: {position: Counter}
    """
    positional = {}
    for i, col in enumerate(["n1", "n2", "n3", "n4", "n5"], 1):
        positional[i] = Counter(df[col].tolist())
    return positional


def consecutive_analysis(df):
    """What % of draws contain consecutive numbers?"""
    consecutive_count = 0
    for _, row in df.iterrows():
        nums = sorted([row["n1"], row["n2"], row["n3"], row["n4"], row["n5"]])
        for i in range(len(nums) - 1):
            if nums[i + 1] - nums[i] == 1:
                consecutive_count += 1
                break
    pct = (consecutive_count / len(df)) * 100
    return pct, consecutive_count


def even_odd_analysis(df):
    """Breakdown of even vs odd numbers in draws."""
    even_counts = []
    for _, row in df.iterrows():
        nums = [row["n1"], row["n2"], row["n3"], row["n4"], row["n5"]]
        evens = sum(1 for n in nums if n % 2 == 0)
        even_counts.append(evens)
    dist = Counter(even_counts)
    return dict(sorted(dist.items()))


def sum_analysis(df):
    """Distribution of the sum of the 5 main numbers."""
    sums = []
    for _, row in df.iterrows():
        s = row["n1"] + row["n2"] + row["n3"] + row["n4"] + row["n5"]
        sums.append(s)
    return {
        "mean": float(np.mean(sums)),
        "median": float(np.median(sums)),
        "std": float(np.std(sums)),
        "min": int(min(sums)),
        "max": int(max(sums)),
        "common_range": (int(np.percentile(sums, 25)), int(np.percentile(sums, 75))),
    }


def decade_frequency(df):
    """
    Frequency by decade group: 1–9, 10–19, 20–29, 30–39, 40–49, 50–59, 60–69.
    Returns dict: {'01-09': count, ...}
    """
    decade_counts = defaultdict(int)
    for _, row in df.iterrows():
        for col in ["n1", "n2", "n3", "n4", "n5"]:
            n = row[col]
            bucket = f"{(n // 10) * 10 + 1:02d}-{min((n // 10 + 1) * 10, 69):02d}"
            decade_counts[bucket] += 1
    return dict(sorted(decade_counts.items()))


def trend_analysis(df, window=100):
    """
    Compare number frequencies in the most recent `window` draws vs all-time.
    Returns list of (number, recent_freq, alltime_freq, trend) sorted by trend desc.
    Trend > 0 means the number is rising in popularity.
    """
    total = len(df)
    recent = df.tail(window)

    all_nums = []
    for col in ["n1", "n2", "n3", "n4", "n5"]:
        all_nums.extend(df[col].tolist())

    recent_nums = []
    for col in ["n1", "n2", "n3", "n4", "n5"]:
        recent_nums.extend(recent[col].tolist())

    all_freq = Counter(all_nums)
    recent_freq = Counter(recent_nums)

    results = []
    expected_per_draw = 5 / 69
    for n in range(1, 70):
        alltime_rate = all_freq.get(n, 0) / (total * 5)
        recent_rate = recent_freq.get(n, 0) / (window * 5)
        trend = recent_rate - alltime_rate
        results.append((n, recent_freq.get(n, 0), all_freq.get(n, 0), round(trend, 5)))

    return sorted(results, key=lambda x: x[3], reverse=True)


def full_analysis(draws):
    """Run all analyses and return a comprehensive report dict."""
    df = build_dataframe(draws)

    report = {
        "total_draws": len(df),
        "date_range": (df["date"].min().strftime("%Y-%m-%d"), df["date"].max().strftime("%Y-%m-%d")),
        "frequency": frequency_analysis(df),
        "powerball_frequency": powerball_frequency(df),
        "gaps": gap_analysis(df),
        "powerball_gaps": powerball_gap_analysis(df),
        "hot_numbers": hot_cold_numbers(df)[0],
        "cold_numbers": hot_cold_numbers(df)[1],
        "pb_hot": powerball_hot_cold(df)[0],
        "pb_cold": powerball_hot_cold(df)[1],
        "top_pairs": pair_analysis(df),
        "positional": positional_analysis(df),
        "consecutive_pct": consecutive_analysis(df),
        "even_odd_dist": even_odd_analysis(df),
        "sum_stats": sum_analysis(df),
        "decade_freq": decade_frequency(df),
        "trends": trend_analysis(df),
        "df": df,
    }
    return report
