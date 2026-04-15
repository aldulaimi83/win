# How to Use the Powerball Analysis Bot

## Method 1: Command Line (CLI)

### Basic Usage

```bash
python main.py
```

This runs the full pipeline:
1. Loads/generates data (2,080 Powerball draws)
2. Runs 9 statistical analyses
3. Generates 9 charts
4. Creates predictions using 5 strategies
5. Displays formatted results

### Command Options

**Generate more predictions:**
```bash
python main.py --tickets 10
```
Creates 10 tickets per strategy instead of default 5.

**Skip chart generation (faster):**
```bash
python main.py --no-charts
```

**Predictions only (skip analysis):**
```bash
python main.py --predictions-only
```

**Generate consensus picks:**
```bash
python main.py --consensus
```
Runs 1,000 simulations to find the "most likely" numbers across all strategies.

**Refresh data:**
```bash
python main.py --refresh
```
Re-downloads/generates fresh historical data instead of using cached CSV.

**Combine options:**
```bash
python main.py --consensus --tickets 5 --no-charts --predictions-only
```

## Method 2: Web UI (Browser)

### Start the Web Server

```bash
python app.py
```

Then open your browser to:
```
http://localhost:5000
```

### Features in Web UI

- **Quick Analysis** — Run analysis and see results immediately
- **5 Prediction Strategies** — Each generates N tickets
- **Interactive Charts** — View all 9 analytical charts
- **Live Statistics** — Frequency tables, hot/cold numbers, trends
- **Copy to Clipboard** — Easy copy of predicted numbers
- **Consensus Mode** — Run 1,000-simulation consensus
- **Download Data** — Export results as CSV

## Method 3: Python Script

Import the modules in your own Python code:

```python
from fetcher import get_data
from analyzer import full_analysis
from predictor import generate_predictions, consensus_pick

# Get data
draws = get_data()

# Analyze
report = full_analysis(draws)

# Predict
predictions = generate_predictions(report, n_tickets=5)
consensus = consensus_pick(report, n_tickets=5)

# Use the results
for strategy, tickets in predictions.items():
    print(f"\n{strategy}")
    for i, (mains, pb) in enumerate(tickets, 1):
        print(f"  Ticket {i}: {' '.join(f'{n:02d}' for n in mains)} | PB: {pb:02d}")
```

## Understanding the Output

### Analysis Tables

**Top 20 Most Drawn Numbers**
- Shows which numbers appear most frequently
- Numbers with higher % have appeared more often historically

**Hot & Cold Numbers (Last 50 Draws)**
- **Hot**: Appeared frequently in the last 50 draws (momentum)
- **Cold**: Haven't appeared recently (potentially "due")

**Most Overdue Numbers**
- Numbers that haven't appeared in a long time
- Gap = number of draws since last appearance
- Months = approximate time (3.5 draws per month)

**Top Number Pairs**
- Numbers that tend to appear together
- Useful for understanding co-occurrence patterns

**Trending Numbers**
- **Rising**: Appearing more often recently
- **Falling**: Appearing less often recently
- Trend score shows the strength of the trend

### Prediction Strategies

**1. Frequency (Hot Numbers)**
- Uses all-time draw frequency
- Favors numbers that have appeared most often
- Conservative approach based on historical averages

**2. Due Numbers (Overdue)**
- Weights by "gap" (how long since appearing)
- Favors numbers that haven't appeared in a long time
- Based on gambler's fallacy (not mathematically sound)

**3. Balanced (Freq + Due + Trend)**
- Blends three factors: 40% frequency, 30% due, 30% trend
- Best overall mix of approaches
- Recommended starting point

**4. Sum-Constrained**
- Ensures sum of 5 numbers falls in historical range (143–204)
- Picks that match typical draw patterns
- Good if you believe sum distributions matter

**5. Top Pairs Seed**
- Seeds predictions with most co-occurring pairs
- Fill remaining slots with frequency weighting
- Incorporates number relationships

### Charts Explained

**freq_main.png** — All-time frequency of each number (1–69)
- Red bars = hot (above average)
- Blue bars = cold (below average)

**freq_powerball.png** — Powerball number frequencies (1–26)

**hot_cold.png** — Comparison of hot vs cold in recent 50 draws

**gaps.png** — How overdue each number is
- Red = very overdue
- Green = recently appeared

**even_odd.png** — Distribution of even vs odd numbers in draws

**decade_freq.png** — Frequency by number groups (1–10, 11–20, etc.)

**sum_dist.png** — Distribution of the sum of 5 numbers
- Red zone = historically common range

**trends.png** — Rising vs falling numbers
- Green bars = trending up
- Red bars = trending down

## Examples

### Example 1: Quick Predictions (30 seconds)
```bash
python main.py --predictions-only --tickets 3
```
Output: 3 tickets from each of 5 strategies = 15 total options

### Example 2: Full Analysis with Consensus (2 minutes)
```bash
python main.py --consensus --tickets 5
```
Output: Full statistics + 5 consensus picks based on 1,000 simulations

### Example 3: Web Dashboard
```bash
python app.py
```
Open http://localhost:5000 and click "Run Full Analysis"

### Example 4: Use in Your Code
```python
from analyzer import frequency_analysis, hot_cold_numbers
from fetcher import get_data

draws = get_data()
freq = frequency_analysis(draws)
hot, cold = hot_cold_numbers(draws)

print("Top 5 most frequent numbers:", sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5])
print("Top 5 hot numbers:", hot[:5])
```

## Data Caching

The bot caches data in `powerball_history.csv` for speed:
- First run: generates/downloads data (~1-2 seconds)
- Subsequent runs: loads from cache (~0.1 seconds)
- Use `--refresh` to update cache

## System Requirements

- Python 3.7+
- ~50MB disk space (data + charts)
- No internet required (uses synthetic data if offline)

## Troubleshooting

**"No data available"**
- Run with `--refresh` to regenerate
- Ensure Python has write permissions to the directory

**Charts not generating**
- Install matplotlib: `pip install matplotlib`
- Ensure `./charts/` directory is writable

**Web UI won't start**
- Install Flask: `pip install flask`
- Port 5000 in use? Try: `python app.py --port 8080`

**Unicode errors on Windows**
- Already fixed in current version
- If issues persist, use `python main.py --no-charts`

## Tips & Tricks

1. **Run predictions frequently** to see how numbers shift over time
2. **Compare strategies** — different strategies favor different numbers
3. **Use consensus mode** when you want a single recommendation
4. **Check trends** — recently trending numbers might be worth including
5. **Don't over-optimize** — remember, lottery is random!

## Important Reminders

⚠️ **Lottery numbers are completely random.** These predictions offer:
- ✓ Interesting statistical analysis
- ✓ Understanding of historical patterns
- ✗ NO advantage for picking winning numbers
- ✗ NO predictive power

Every draw is independent. Past patterns don't predict future results.

**Play responsibly!** Treat lottery as entertainment, not investment.
