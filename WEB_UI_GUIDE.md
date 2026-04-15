# Web UI - Quick Start Guide

## Installation

First, install Flask:
```bash
pip install flask
```

Or update all requirements:
```bash
pip install -r requirements.txt
```

## Starting the Web Server

Run the Flask app:
```bash
python app.py
```

You should see:
```
============================================================
  Powerball Analysis Bot - Web Dashboard
  Open: http://localhost:5000
============================================================
```

Then open your browser to: **http://localhost:5000**

## Using the Web Dashboard

### 1. Control Panel

At the top, you'll find:

- **Tickets/Strategy Selector**: Choose how many tickets each strategy generates
  - 3 (Quick - 15 total)
  - 5 (Default - 25 total)
  - 10 (Comprehensive - 50 total)

- **Generate Charts**: Toggle to include/exclude chart generation
  - Checked = slower but prettier output
  - Unchecked = faster analysis

- **Consensus Mode**: Run 1,000-simulation consensus
  - Unchecked = faster (2-3 seconds)
  - Checked = slower (1-2 minutes) but more reliable

- **Run Analysis Button**: Click to start the analysis
  - Shows real-time progress
  - Updates status as it runs

### 2. Statistics Tab

Shows comprehensive statistical analysis:

**Overview Cards**
- Total draws analyzed
- Date range (start & end)
- % of draws with consecutive numbers
- Average sum of 5 balls
- Common sum range

**Top 20 Main Numbers**
- Most frequently drawn numbers
- Count and percentage

**Top 10 Powerball Numbers**
- Most frequently drawn Powerball
- Count and percentage

**Hot Numbers (Recent)**
- Numbers drawn frequently in last 50 draws
- Colored badges with frequency count

**Cold Numbers (Recent)**
- Numbers that haven't appeared recently
- Good candidates for "due" numbers

**Most Overdue Numbers**
- Numbers with largest gaps
- Shows gaps in draws and approximate months overdue

**Top Number Pairs**
- Numbers that frequently appear together
- Co-occurrence count

**Trending Numbers**
- Rising: Appearing more frequently recently
- Falling: Appearing less frequently recently
- Trend scores show strength

### 3. Predictions Tab

Displays all predictions from 5 strategies:

**Frequency (Hot Numbers)**
- Favors all-time hot numbers
- Conservative, based on averages
- Good for reliable patterns

**Due Numbers (Overdue)**
- Weights numbers that haven't appeared
- Based on gambler's fallacy (not scientific)
- Interesting but not proven effective

**Balanced (Freq + Due + Trend)**
- Best overall mix
- 40% frequency + 30% due + 30% trend
- **Recommended starting point**

**Sum-Constrained**
- Ensures sum falls in historical range (143-204)
- Picks that match typical draw patterns
- For sum-believers

**Top Pairs Seed**
- Seeds with most co-occurring pairs
- Incorporates number relationships
- Unique approach

**Consensus Picks** (if enabled)
- Numbers appearing most in 1,000 simulations
- Represents the "wisdom of crowds"
- Most stable predictions
- **Slowest but most reliable**

Each ticket shows:
- 5 main numbers
- Powerball number
- Copy button for easy clipboard copying

### 4. Charts Tab

9 different analytical charts:

1. **freq_main.png** — Main number frequencies (1-69)
   - Red bars = above average (hot)
   - Blue bars = below average (cold)

2. **freq_powerball.png** — Powerball frequencies (1-26)

3. **hot_cold.png** — Comparison of recent hot vs cold

4. **gaps.png** — How overdue each number is
   - Red = very overdue
   - Green = recently appeared

5. **gaps_pb.png** — Powerball overdue status

6. **even_odd.png** — Distribution of even vs odd

7. **decade_freq.png** — Frequency by number groups
   - Shows if certain ranges are favored

8. **sum_dist.png** — Distribution of sum of 5 numbers
   - Red zone = historically common

9. **trends.png** — Rising vs falling numbers

## Features

### Copy to Clipboard
Click the "Copy" button next to any ticket to copy the entire ticket (numbers + powerball) to your clipboard.

### Multiple Strategies
Compare results from 5 different approaches:
- If all strategies agree on a number, it's statistically strong
- If they disagree, it's more debatable

### Real-Time Progress
Watch the analysis progress in real-time:
- 20% — Data loaded
- 50% — Analysis complete
- 70% — Predictions generated
- 100% — Charts done

### No Page Refresh
All results display dynamically without page reload.

## Tips

### Fastest Results
```
Tickets: 3
Charts: Unchecked
Consensus: Unchecked
Time: ~10 seconds
```

### Balanced Results
```
Tickets: 5
Charts: Checked
Consensus: Unchecked
Time: ~30 seconds
```

### Most Comprehensive
```
Tickets: 10
Charts: Checked
Consensus: Checked
Time: ~3-4 minutes
```

## Keyboard Shortcuts

- `Tab` — Navigate between form fields
- `Enter` — Click Run Analysis button
- `Ctrl+C` on tabs — Copy ticket numbers
- `Click & Scroll` — Scroll through large tables

## Troubleshooting

**Port Already in Use**
```bash
python app.py --port 8080
```

**Page Not Loading**
- Make sure Flask is installed: `pip install flask`
- Check console for error messages
- Try refreshing the page (Ctrl+F5)

**Analysis Taking Too Long**
- Uncheck "Generate Charts"
- Uncheck "Consensus Mode"
- Lower ticket count to 3

**Charts Not Showing**
- Make sure analysis is complete (progress bar at 100%)
- Check that `charts/` directory exists
- Try running again

## Advanced Usage

### Custom Port
```bash
python app.py --port 8080
```

### Bind to External IP
```bash
python app.py --host 0.0.0.0 --port 5000
```
Then access from another computer at: `http://YOUR_IP:5000`

### Disable Auto-Reload
```bash
python app.py
```

## API Endpoints

For developers who want to integrate with other tools:

**GET /api/status**
```json
{
  "running": false,
  "progress": 100,
  "status": "Complete!"
}
```

**POST /api/run-analysis**
```json
{
  "tickets": 5,
  "charts": true,
  "consensus": false
}
```

**GET /api/results**
Returns full analysis data (statistics, frequencies, trends)

**GET /api/predictions**
Returns all predictions and consensus picks

**GET /api/charts**
Returns list of available chart files

## Remember!

⚠️ **Lottery numbers are random.** This dashboard is for analytical interest and entertainment only. It provides no predictive advantage over random selection.

Play responsibly!
