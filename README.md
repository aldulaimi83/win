# Powerball Statistical Analysis Bot

A comprehensive Python tool that analyzes 20 years of Powerball historical data, identifies patterns, and generates statistically-weighted number predictions.

## Features

- **20-Year Historical Analysis**: Analyzes 2,000+ Powerball draws (2004–2026)
- **9 Statistical Analyses**:
  - Main number frequency analysis
  - Powerball number frequency
  - Gap analysis (overdue numbers)
  - Hot & cold numbers (recent 50 draws)
  - Number pair analysis (co-occurrences)
  - Positional analysis
  - Even/odd distribution
  - Sum distribution
  - Trend analysis (rising vs falling)

- **5 Prediction Strategies**:
  1. **Frequency (Hot Numbers)**: Favors numbers drawn most often
  2. **Due Numbers (Overdue)**: Weights numbers that haven't appeared in a long time
  3. **Balanced**: Blends frequency, due dates, and trends (40% / 30% / 30%)
  4. **Sum-Constrained**: Ensures picks fall in historically common sum ranges
  5. **Top Pairs Seed**: Seeds picks with commonly co-occurring number pairs

- **Consensus Picks**: Run 1,000+ simulations to find numbers appearing most often
- **Rich CLI Output**: Beautiful tables and formatted reports
- **Chart Generation**: 9+ analytical charts (PNG)

## Important Disclaimer

**Lottery numbers are randomly drawn.** Statistical analysis cannot predict future results. Each draw is an independent event with no relationship to previous draws. These predictions are for analytical interest only and offer no advantage over random selection.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Full Analysis with Predictions
```bash
python main.py
```

### Predictions Only (Skip Analysis)
```bash
python main.py --predictions-only
```

### Generate More Tickets Per Strategy
```bash
python main.py --tickets 10
```

### Skip Chart Generation
```bash
python main.py --no-charts
```

### Generate Consensus Picks (1,000-run simulation)
```bash
python main.py --consensus
```

### Refresh Data (Re-download/Generate Fresh Dataset)
```bash
python main.py --refresh
```

### Combine Options
```bash
python main.py --consensus --tickets 5 --no-charts
```

## Output

The bot generates:

1. **Console Report**: Formatted tables with all statistical findings
2. **CSV File**: `powerball_history.csv` — Full historical dataset
3. **Charts** (in `./charts/`):
   - `freq_main.png` — Main number frequency (all-time)
   - `freq_powerball.png` — Powerball frequency
   - `hot_cold.png` — Hot vs cold numbers (recent)
   - `gaps.png` — Overdue numbers (main balls)
   - `gaps_pb.png` — Overdue powerballs
   - `even_odd.png` — Even/odd distribution
   - `decade_freq.png` — Frequency by number group
   - `sum_dist.png` — Sum of 5 balls distribution
   - `trends.png` — Rising vs falling numbers

## Data Source

The bot:
1. Attempts to fetch official Powerball data from powerball.com API
2. Falls back to public CSV datasets if API is unavailable
3. Falls back to generating realistic synthetic data if both fail

This ensures the tool works in any environment (online or offline).

## Project Structure

```
win/
├── main.py                      # CLI entry point
├── fetcher.py                   # Data fetching/loading
├── analyzer.py                  # Statistical analysis engine
├── predictor.py                 # Prediction strategies
├── visualizer.py                # Chart generation
├── synthetic_data_generator.py   # Synthetic data creation
├── requirements.txt             # Dependencies
├── powerball_history.csv        # Cached historical data (auto-generated)
└── charts/                      # Generated PNG charts (auto-created)
```

## How It Works

### 1. Data Collection
- Tries to fetch real Powerball data from official sources
- Falls back to synthetic dataset if online unavailable
- Caches data locally in CSV

### 2. Analysis
Computes 9 different statistical measures:
- Frequencies (how often each number appears)
- Gaps (how long since each number last appeared)
- Hot/cold streaks
- Pair analysis
- Distribution stats
- Trends

### 3. Prediction
Generates picks using 5 different strategies, each with different weights:
- **Frequency Strategy**: All-time draw frequency
- **Due Strategy**: Gaps (overdue numbers)
- **Balanced**: Blend of frequency, due, and trends
- **Sum-Constrained**: Picks that match historical sum patterns
- **Pairs**: Uses top co-occurring pairs as seeds

### 4. Visualization
Generates 9 charts showing:
- Frequency distributions
- Hot/cold patterns
- Overdue numbers
- Even/odd ratios
- Sum ranges
- Trends

## Example Output

```
TOP 20 MOST DRAWN MAIN NUMBERS
+-------+--------+----------+----------+
| Rank  | Number | Frequency| % of All |
+-------+--------+----------+----------+
|   1   |   23   |   176    |   8.5%   |
|   2   |   32   |   175    |   8.4%   |
|   3   |   41   |   169    |   8.1%   |
...

PREDICTED TICKETS

Frequency (Hot Numbers)
  Ticket 1: 13  21  33  52  56  PB: 06
  Ticket 2: 03  06  19  32  68  PB: 21

Due Numbers (Overdue)
  Ticket 1: 04  07  44  46  54  PB: 03
  Ticket 2: 03  18  46  63  66  PB: 02
```

## Technical Details

### Dependencies
- `requests` — Data fetching
- `beautifulsoup4` — Web scraping
- `pandas` — Data manipulation
- `numpy` — Numerical calculations
- `matplotlib` — Chart generation
- `rich` — CLI formatting

### Python Version
Requires Python 3.7+

## Limitations

1. **No Predictive Power**: Lottery draws are random. Statistical patterns cannot predict future results.
2. **Historical Bias**: Past patterns don't inform future draws.
3. **Independence**: Each draw is independent with no memory of previous results.
4. **Gambler's Fallacy**: "Due numbers" are not more likely to appear despite gaps.

## Fun Fact

If you played every possible Powerball combination (292,201,338 tickets), the expected jackpot payout would be ~$100M, making it unprofitable even with a guaranteed win!

## License

MIT

## Author

Built with Claude Code

---

**Remember**: Play responsibly. Treat lottery tickets as entertainment, not investment!
