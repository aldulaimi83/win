"""
Powerball Analysis Bot
======================
Analyzes 20 years of Powerball history and generates statistically-weighted predictions.

Usage:
    python main.py                    # Full analysis + predictions
    python main.py --refresh          # Re-download fresh data
    python main.py --tickets 10       # Generate 10 tickets per strategy
    python main.py --no-charts        # Skip chart generation
    python main.py --consensus        # Show consensus picks
"""

import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.rule import Rule

import fetcher
import analyzer
import predictor
import visualizer

console = Console()


def format_ticket(mains, pb):
    nums = "  ".join(f"[bold white]{n:02d}[/bold white]" for n in mains)
    return f"{nums}  [bold red]PB: {pb:02d}[/bold red]"


def print_header():
    console.print()
    console.print(Panel.fit(
        "[bold yellow]POWERBALL STATISTICAL ANALYSIS BOT[/bold yellow]\n"
        "[dim]20 Years of Historical Data Analysis[/dim]",
        border_style="yellow",
        padding=(1, 4),
    ))
    console.print()
    console.print(
        "[bold red]DISCLAIMER:[/bold red] [dim]Lottery draws are random events. "
        "Statistical analysis cannot predict future results. "
        "Play responsibly.[/dim]"
    )
    console.print()


def print_overview(report):
    console.print(Rule("[bold cyan]DATA OVERVIEW[/bold cyan]"))
    console.print(f"  Total draws analyzed : [bold]{report['total_draws']:,}[/bold]")
    console.print(f"  Date range           : [bold]{report['date_range'][0]}[/bold] to [bold]{report['date_range'][1]}[/bold]")

    cs_pct, cs_count = report["consecutive_pct"]
    console.print(f"  Draws with consecutive numbers: [bold]{cs_count:,}[/bold] ([bold]{cs_pct:.1f}%[/bold])")

    ss = report["sum_stats"]
    console.print(
        f"  Sum of 5 balls — Mean: [bold]{ss['mean']:.1f}[/bold]  "
        f"Std: [bold]{ss['std']:.1f}[/bold]  "
        f"Common range: [bold]{ss['common_range'][0]}–{ss['common_range'][1]}[/bold]"
    )
    console.print()


def print_frequency_table(report):
    console.print(Rule("[bold cyan]TOP 20 MOST DRAWN MAIN NUMBERS[/bold cyan]"))
    freq = report["frequency"]
    top20 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Number", justify="center", width=8)
    table.add_column("Times Drawn", justify="right", width=14)
    table.add_column("% of Draws", justify="right", width=12)

    total = report["total_draws"]
    for i, (n, c) in enumerate(top20, 1):
        pct = (c / total) * 100
        table.add_row(str(i), f"[bold]{n:02d}[/bold]", str(c), f"{pct:.1f}%")
    console.print(table)

    console.print(Rule("[bold cyan]TOP 10 POWERBALL NUMBERS[/bold cyan]"))
    pb_freq = report["powerball_frequency"]
    pb_top10 = sorted(pb_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    pb_table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    pb_table.add_column("Rank", style="dim", width=6)
    pb_table.add_column("Powerball", justify="center", width=10)
    pb_table.add_column("Times Drawn", justify="right", width=14)
    pb_table.add_column("% of Draws", justify="right", width=12)

    for i, (n, c) in enumerate(pb_top10, 1):
        pct = (c / total) * 100
        pb_table.add_row(str(i), f"[bold red]{n:02d}[/bold red]", str(c), f"{pct:.1f}%")
    console.print(pb_table)


def print_hot_cold(report):
    console.print(Rule("[bold cyan]HOT & COLD NUMBERS (Last 50 Draws)[/bold cyan]"))
    hot = report["hot_numbers"]
    cold = report["cold_numbers"]
    pb_hot = report["pb_hot"]

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Hot Number", justify="center", style="bold red", width=12)
    table.add_column("Freq", justify="right", width=6)
    table.add_column("Cold Number", justify="center", style="bold blue", width=12)
    table.add_column("Freq", justify="right", width=6)

    for i in range(min(10, len(hot), len(cold))):
        hn, hc = hot[i]
        cn, cc = cold[i]
        table.add_row(str(i + 1), f"{hn:02d}", str(hc), f"{cn:02d}", str(cc))
    console.print(table)

    console.print()
    pb_hot_str = "  ".join(f"[bold red]{n:02d}[/bold red]({c})" for n, c in pb_hot[:5])
    console.print(f"  Hot Powerballs: {pb_hot_str}")


def print_gaps(report):
    console.print(Rule("[bold cyan]MOST OVERDUE NUMBERS[/bold cyan]"))
    gaps = report["gaps"]
    top_gap = sorted(gaps.items(), key=lambda x: x[1], reverse=True)[:15]

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    table.add_column("Number", justify="center", width=10)
    table.add_column("Draws Since Last Seen", justify="right", width=22)
    table.add_column("Approx. Months Overdue", justify="right", width=24)

    for n, g in top_gap:
        months = round(g * 3.5 / 30, 1)  # ~3.5 draws/month
        table.add_row(f"[bold]{n:02d}[/bold]", str(g), f"~{months}")
    console.print(table)

    pb_gaps = report["powerball_gaps"]
    top_pb_gap = sorted(pb_gaps.items(), key=lambda x: x[1], reverse=True)[:5]
    pb_str = "  ".join(f"[bold red]{n:02d}[/bold red]({g} draws)" for n, g in top_pb_gap)
    console.print(f"\n  Most overdue Powerballs: {pb_str}")


def print_top_pairs(report):
    console.print(Rule("[bold cyan]TOP 10 NUMBER PAIRS[/bold cyan]"))
    pairs = report["top_pairs"][:10]

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Pair", justify="center", width=12)
    table.add_column("Times Together", justify="right", width=16)

    for i, ((a, b), c) in enumerate(pairs, 1):
        table.add_row(str(i), f"[bold]{a:02d}[/bold] + [bold]{b:02d}[/bold]", str(c))
    console.print(table)


def print_trends(report):
    console.print(Rule("[bold cyan]TRENDING NUMBERS (Rising vs Falling)[/bold cyan]"))
    trends = report["trends"]
    rising = trends[:10]
    falling = trends[-10:][::-1]

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    table.add_column("Rising Numbers", justify="center", style="bold green", width=16)
    table.add_column("Trend", justify="right", width=10)
    table.add_column("Falling Numbers", justify="center", style="bold red", width=16)
    table.add_column("Trend", justify="right", width=10)

    for i in range(10):
        rn, _, _, rt = rising[i]
        fn, _, _, ft = falling[i]
        table.add_row(f"{rn:02d}", f"+{rt*1000:.2f}", f"{fn:02d}", f"{ft*1000:.2f}")
    console.print(table)


def print_even_odd(report):
    console.print(Rule("[bold cyan]EVEN / ODD DISTRIBUTION[/bold cyan]"))
    dist = report["even_odd_dist"]
    total = sum(dist.values())
    for k, v in sorted(dist.items()):
        bar = "#" * int((v / total) * 40)
        pct = (v / total) * 100
        console.print(f"  {k} Even / {5-k} Odd  [{bar:<40}] {pct:.1f}%")


def print_decade_freq(report):
    console.print(Rule("[bold cyan]FREQUENCY BY NUMBER GROUP[/bold cyan]"))
    decade = report["decade_freq"]
    total = sum(decade.values())
    for label, count in decade.items():
        bar = "#" * int((count / total) * 40)
        pct = (count / total) * 100
        console.print(f"  {label}  [{bar:<40}] {pct:.1f}%  ({count:,} appearances)")


def print_predictions(predictions, consensus=None):
    console.print()
    console.print(Rule("[bold yellow]PREDICTED TICKETS[/bold yellow]"))
    console.print(
        "[dim]Generated using 5 different statistical strategies. "
        "Numbers are weighted by historical patterns.[/dim]\n"
    )

    for strategy, tickets in predictions.items():
        console.print(f"  [bold cyan]{strategy}[/bold cyan]")
        for i, (mains, pb) in enumerate(tickets, 1):
            console.print(f"    Ticket {i}: {format_ticket(mains, pb)}")
        console.print()

    if consensus:
        console.print(Rule("[bold yellow]CONSENSUS PICKS (1,000-run simulation)[/bold yellow]"))
        console.print("[dim]Numbers that appear most often across many balanced simulations.[/dim]\n")
        for i, (mains, pb) in enumerate(consensus, 1):
            console.print(f"  Pick {i}: {format_ticket(mains, pb)}")
        console.print()


def main():
    parser = argparse.ArgumentParser(description="Powerball Statistical Analysis Bot")
    parser.add_argument("--refresh", action="store_true", help="Re-download fresh data")
    parser.add_argument("--tickets", type=int, default=5, help="Number of tickets per strategy (default: 5)")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation")
    parser.add_argument("--consensus", action="store_true", help="Run consensus simulation (slower)")
    parser.add_argument("--predictions-only", action="store_true", help="Skip analysis, show predictions only")
    args = parser.parse_args()

    print_header()

    # 1. Fetch data
    console.print("[bold]Step 1/4:[/bold] Loading historical data...")
    draws = fetcher.get_data(force_refresh=args.refresh)

    if not draws:
        console.print("[bold red]ERROR: No data available. Try running with --refresh.[/bold red]")
        sys.exit(1)

    console.print(f"  [green][OK][/green] Loaded [bold]{len(draws):,}[/bold] draws.\n")

    # 2. Run analysis
    console.print("[bold]Step 2/4:[/bold] Running statistical analysis...")
    report = analyzer.full_analysis(draws)
    console.print(f"  [green][OK][/green] Analysis complete.\n")

    # 3. Show analysis
    if not args.predictions_only:
        print_overview(report)
        print_frequency_table(report)
        print_hot_cold(report)
        print_gaps(report)
        print_top_pairs(report)
        print_trends(report)
        print_even_odd(report)
        print_decade_freq(report)

    # 4. Generate charts
    if not args.no_charts:
        console.print("\n[bold]Step 3/4:[/bold] Generating charts...")
        try:
            paths = visualizer.generate_all_charts(report)
            console.print(f"  [green][OK][/green] {len(paths)} charts saved to [bold]./charts/[/bold]")
            for p in paths:
                console.print(f"    • {p}")
        except Exception as e:
            console.print(f"  [yellow]Warning: Chart generation failed: {e}[/yellow]")

    # 5. Generate predictions
    console.print("\n[bold]Step 4/4:[/bold] Generating predictions...")
    predictions = predictor.generate_predictions(report, n_tickets=args.tickets)

    consensus = None
    if args.consensus:
        console.print("  Running 1,000-simulation consensus (may take a moment)...")
        consensus = predictor.consensus_pick(report, n_tickets=args.tickets)

    console.print(f"  [green][OK][/green] Predictions ready.\n")

    print_predictions(predictions, consensus)

    console.print(Panel.fit(
        "[bold green]Analysis complete![/bold green]\n"
        "Charts saved to [bold]./charts/[/bold]\n"
        "Run [bold]python main.py --consensus[/bold] for consensus picks.",
        border_style="green",
        padding=(0, 2),
    ))


if __name__ == "__main__":
    main()
