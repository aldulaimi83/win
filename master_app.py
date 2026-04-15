"""
Master Control Panel - Run all analysis bots from one unified GUI
- Standalone JavaScript analysis
- Full statistical analysis
- Web dashboard
- All in one place
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
import threading
from datetime import datetime

app = Flask(__name__, template_folder="master_templates", static_folder="master_static")

# State management
state = {
    "running": False,
    "progress": 0,
    "status": "Ready",
    "results": None,
    "mode": None,
}


@app.route("/")
def index():
    return render_template("master.html")


@app.route("/api/status")
def get_status():
    return jsonify({
        "running": state["running"],
        "progress": state["progress"],
        "status": state["status"],
        "mode": state["mode"],
    })


@app.route("/api/run-analysis", methods=["POST"])
def run_analysis():
    """Run analysis in background thread"""
    if state["running"]:
        return jsonify({"error": "Analysis already running"}), 400

    data = request.json or {}
    mode = data.get("mode", "full")  # full, quick, consensus
    n_tickets = int(data.get("tickets", 5))

    state["running"] = True
    state["mode"] = mode
    state["progress"] = 0
    state["status"] = "Initializing..."

    thread = threading.Thread(
        target=_run_analysis_worker,
        args=(mode, n_tickets),
    )
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Analysis started", "mode": mode})


def _run_analysis_worker(mode, n_tickets):
    """Execute analysis"""
    try:
        state["progress"] = 10
        state["status"] = "Loading modules..."

        # Import here to avoid circular imports
        from fetcher import get_data
        from analyzer import full_analysis
        from predictor import generate_predictions, consensus_pick

        state["progress"] = 20
        state["status"] = "Fetching data..."
        draws = get_data()

        state["progress"] = 40
        state["status"] = "Running analysis..."
        report = full_analysis(draws)

        state["progress"] = 70
        state["status"] = "Generating predictions..."
        predictions = generate_predictions(report, n_tickets=n_tickets)

        consensus = None
        if mode == "consensus":
            state["progress"] = 85
            state["status"] = "Running consensus (1000 simulations)..."
            consensus = consensus_pick(report, n_tickets=n_tickets)

        state["progress"] = 95
        state["status"] = "Formatting results..."

        # Format results
        results = format_results(report, predictions, consensus)
        state["results"] = results

        state["progress"] = 100
        state["status"] = "Complete!"

    except Exception as e:
        state["status"] = f"Error: {str(e)}"
        state["running"] = False
    finally:
        state["running"] = False


def format_results(report, predictions, consensus):
    """Format analysis results for display"""
    return {
        "overview": {
            "total_draws": report["total_draws"],
            "date_range": report["date_range"],
            "consecutive_pct": round(report["consecutive_pct"][0], 1),
            "sum_mean": round(report["sum_stats"]["mean"], 1),
            "sum_std": round(report["sum_stats"]["std"], 1),
        },
        "top_numbers": [
            {"num": n, "count": c, "pct": round((c / report["total_draws"]) * 100, 1)}
            for n, c in sorted(report["frequency"].items(), key=lambda x: x[1], reverse=True)[:20]
        ],
        "top_pb": [
            {"num": n, "count": c}
            for n, c in sorted(report["powerball_frequency"].items(), key=lambda x: x[1], reverse=True)[:10]
        ],
        "hot": [{"num": n, "freq": c} for n, c in report["hot_numbers"][:15]],
        "cold": [{"num": n, "freq": c} for n, c in report["cold_numbers"][:15]],
        "overdue": [
            {"num": n, "gap": g}
            for n, g in sorted(report["gaps"].items(), key=lambda x: x[1], reverse=True)[:10]
        ],
        "predictions": {
            strategy: [
                {"nums": mains, "pb": pb}
                for mains, pb in tickets
            ]
            for strategy, tickets in predictions.items()
        },
        "consensus": [
            {"nums": mains, "pb": pb}
            for mains, pb in consensus
        ] if consensus else None,
    }


@app.route("/api/results")
def get_results():
    """Get formatted results"""
    if not state["results"]:
        return jsonify({"error": "No results available"}), 400
    return jsonify(state["results"])


@app.route("/api/download-csv")
def download_csv():
    """Download results as CSV"""
    if not state["results"]:
        return jsonify({"error": "No results available"}), 400

    import csv
    from io import StringIO

    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)

    results = state["results"]

    # Write predictions
    writer.writerow(["POWERBALL ANALYSIS RESULTS"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([])

    writer.writerow(["PREDICTIONS"])
    writer.writerow([])

    for strategy, tickets in results["predictions"].items():
        writer.writerow([strategy])
        for i, ticket in enumerate(tickets, 1):
            nums = " ".join(f"{n:02d}" for n in ticket["nums"])
            writer.writerow([f"Ticket {i}", nums, f"PB: {ticket['pb']:02d}"])
        writer.writerow([])

    if results["consensus"]:
        writer.writerow(["CONSENSUS PICKS (1000 Simulations)"])
        for i, ticket in enumerate(results["consensus"], 1):
            nums = " ".join(f"{n:02d}" for n in ticket["nums"])
            writer.writerow([f"Pick {i}", nums, f"PB: {ticket['pb']:02d}"])

    csv_content = csv_buffer.getvalue()

    return {
        "filename": f"powerball_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "content": csv_content
    }, 200, {"Content-Disposition": "attachment"}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"  POWERBALL ANALYSIS BOT - MASTER CONTROL PANEL")
    print(f"  Open your browser: http://localhost:{args.port}")
    print(f"{'='*70}\n")

    app.run(debug=False, host=args.host, port=args.port, use_reloader=False)
