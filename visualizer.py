"""
Visualization module: generates charts from the analysis data.
Saves PNG files to the ./charts/ directory.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

CHARTS_DIR = "charts"


def ensure_charts_dir():
    os.makedirs(CHARTS_DIR, exist_ok=True)


def plot_frequency(freq_dict, title="Main Ball Frequency (All Time)", filename="freq_main.png"):
    """Bar chart of how often each number has been drawn."""
    ensure_charts_dir()
    numbers = list(range(1, 70))
    counts = [freq_dict.get(n, 0) for n in numbers]
    avg = sum(counts) / len(counts)

    fig, ax = plt.subplots(figsize=(18, 5))
    colors = ["tomato" if c > avg * 1.1 else ("steelblue" if c < avg * 0.9 else "mediumpurple") for c in counts]
    bars = ax.bar(numbers, counts, color=colors, edgecolor="white", linewidth=0.5)
    ax.axhline(avg, color="gold", linestyle="--", linewidth=1.5, label=f"Average ({avg:.1f})")
    ax.set_xlabel("Ball Number", fontsize=12)
    ax.set_ylabel("Times Drawn", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(numbers[::5])
    ax.legend()
    # Color legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="tomato", label="Hot (>10% above avg)"),
        Patch(facecolor="mediumpurple", label="Normal"),
        Patch(facecolor="steelblue", label="Cold (<10% below avg)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_powerball_frequency(pb_freq, filename="freq_powerball.png"):
    """Bar chart of Powerball number frequencies."""
    ensure_charts_dir()
    numbers = list(range(1, 27))
    counts = [pb_freq.get(n, 0) for n in numbers]
    avg = sum(counts) / len(counts)

    fig, ax = plt.subplots(figsize=(12, 4))
    colors = ["tomato" if c > avg else "steelblue" for c in counts]
    ax.bar(numbers, counts, color=colors, edgecolor="white")
    ax.axhline(avg, color="gold", linestyle="--", linewidth=1.5, label=f"Average ({avg:.1f})")
    ax.set_xlabel("Powerball Number", fontsize=12)
    ax.set_ylabel("Times Drawn", fontsize=12)
    ax.set_title("Powerball Number Frequency", fontsize=14, fontweight="bold")
    ax.set_xticks(numbers)
    ax.legend()
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_hot_cold(hot, cold, filename="hot_cold.png"):
    """Horizontal bar chart comparing hot vs cold numbers."""
    ensure_charts_dir()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    hot_nums = [str(n) for n, _ in hot[:15]]
    hot_counts = [c for _, c in hot[:15]]
    axes[0].barh(hot_nums, hot_counts, color="tomato", edgecolor="white")
    axes[0].set_title("Top 15 Hot Numbers (Last 50 Draws)", fontweight="bold")
    axes[0].set_xlabel("Frequency")
    axes[0].invert_yaxis()

    cold_nums = [str(n) for n, _ in cold[:15]]
    cold_counts = [c for _, c in cold[:15]]
    axes[1].barh(cold_nums, cold_counts, color="steelblue", edgecolor="white")
    axes[1].set_title("Top 15 Cold Numbers (Last 50 Draws)", fontweight="bold")
    axes[1].set_xlabel("Frequency")
    axes[1].invert_yaxis()

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_gap_analysis(gaps, title="Draws Since Last Appearance", filename="gaps.png"):
    """Chart showing how overdue each number is."""
    ensure_charts_dir()
    numbers = list(range(1, 70))
    gap_values = [gaps.get(n, 0) for n in numbers]
    max_gap = max(gap_values)
    colors = plt.cm.RdYlGn_r([g / max_gap for g in gap_values])

    fig, ax = plt.subplots(figsize=(18, 5))
    ax.bar(numbers, gap_values, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_xlabel("Ball Number", fontsize=12)
    ax.set_ylabel("Draws Since Last Seen", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(numbers[::5])
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_even_odd(dist, filename="even_odd.png"):
    """Pie/bar chart of even/odd distribution."""
    ensure_charts_dir()
    labels = [f"{k} Even, {5-k} Odd" for k in dist.keys()]
    values = list(dist.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=plt.cm.Paired.colors[:len(labels)], edgecolor="white")
    ax.set_title("Even/Odd Distribution in Draws", fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Draws")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_decade_freq(decade_freq, filename="decade_freq.png"):
    """Frequency by number decade group."""
    ensure_charts_dir()
    labels = list(decade_freq.keys())
    values = list(decade_freq.values())

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(labels, values, color="mediumpurple", edgecolor="white")
    ax.set_title("Frequency by Number Group", fontsize=13, fontweight="bold")
    ax.set_ylabel("Total Appearances")
    ax.set_xlabel("Number Range")
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_sum_distribution(df, sum_stats, filename="sum_dist.png"):
    """Histogram of draw sums with the common range highlighted."""
    ensure_charts_dir()
    sums = (df["n1"] + df["n2"] + df["n3"] + df["n4"] + df["n5"]).tolist()
    low, high = sum_stats["common_range"]

    fig, ax = plt.subplots(figsize=(10, 5))
    n, bins, patches = ax.hist(sums, bins=50, color="steelblue", edgecolor="white", alpha=0.8)
    # Highlight common range
    for patch, left in zip(patches, bins[:-1]):
        if low <= left <= high:
            patch.set_facecolor("tomato")
    ax.axvline(sum_stats["mean"], color="gold", linestyle="--", label=f'Mean: {sum_stats["mean"]:.1f}')
    ax.set_xlabel("Sum of 5 Main Numbers", fontsize=12)
    ax.set_ylabel("Number of Draws", fontsize=12)
    ax.set_title("Distribution of Draw Sums (Red = Common Range)", fontsize=13, fontweight="bold")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_trend(trends, filename="trends.png"):
    """Show which numbers are trending up vs down recently."""
    ensure_charts_dir()
    # Top 15 rising and top 15 falling
    rising = trends[:15]
    falling = trends[-15:][::-1]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    r_nums = [str(n) for n, _, _, _ in rising]
    r_vals = [t * 1000 for _, _, _, t in rising]
    axes[0].barh(r_nums, r_vals, color="tomato", edgecolor="white")
    axes[0].set_title("Top 15 Rising Trends", fontweight="bold")
    axes[0].set_xlabel("Trend Score (×1000)")
    axes[0].invert_yaxis()

    f_nums = [str(n) for n, _, _, _ in falling]
    f_vals = [abs(t) * 1000 for _, _, _, t in falling]
    axes[1].barh(f_nums, f_vals, color="steelblue", edgecolor="white")
    axes[1].set_title("Top 15 Falling Trends", fontweight="bold")
    axes[1].set_xlabel("Trend Score (×1000)")
    axes[1].invert_yaxis()

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def generate_all_charts(report):
    """Generate and save all charts. Returns list of file paths."""
    paths = []
    df = report["df"]
    paths.append(plot_frequency(report["frequency"]))
    paths.append(plot_powerball_frequency(report["powerball_frequency"]))
    paths.append(plot_hot_cold(report["hot_numbers"], report["cold_numbers"]))
    paths.append(plot_gap_analysis(report["gaps"]))
    paths.append(plot_gap_analysis(report["powerball_gaps"], "Powerball Draws Since Last Appearance", "gaps_pb.png"))
    paths.append(plot_even_odd(report["even_odd_dist"]))
    paths.append(plot_decade_freq(report["decade_freq"]))
    paths.append(plot_sum_distribution(df, report["sum_stats"]))
    paths.append(plot_trend(report["trends"]))
    return paths
