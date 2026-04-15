"""
Web UI for the Powerball Analysis Bot
Provides an interactive dashboard to run analysis and view predictions
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import threading
from fetcher import get_data
from analyzer import full_analysis
from predictor import generate_predictions, consensus_pick
from visualizer import generate_all_charts

app = Flask(__name__, template_folder="templates", static_folder="static")

# Global state
analysis_state = {
    "running": False,
    "progress": 0,
    "status": "Ready",
    "report": None,
    "predictions": None,
    "consensus": None,
}


@app.route("/")
def index():
    """Serve the main dashboard"""
    return render_template("index.html")


@app.route("/api/status")
def status():
    """Get current analysis status"""
    return jsonify({
        "running": analysis_state["running"],
        "progress": analysis_state["progress"],
        "status": analysis_state["status"],
    })


@app.route("/api/run-analysis", methods=["POST"])
def run_analysis():
    """Run full analysis in background"""
    if analysis_state["running"]:
        return jsonify({"error": "Analysis already running"}), 400

    data = request.json or {}
    n_tickets = int(data.get("tickets", 5))
    include_charts = data.get("charts", True)
    consensus_mode = data.get("consensus", False)

    # Run in background thread
    thread = threading.Thread(
        target=_run_analysis_worker,
        args=(n_tickets, include_charts, consensus_mode),
    )
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Analysis started"})


def _run_analysis_worker(n_tickets, include_charts, consensus_mode):
    """Background worker for analysis"""
    try:
        analysis_state["running"] = True
        analysis_state["progress"] = 0
        analysis_state["status"] = "Loading data..."

        # 1. Fetch data
        draws = get_data()
        analysis_state["progress"] = 20
        analysis_state["status"] = "Analyzing statistics..."

        # 2. Analyze
        report = full_analysis(draws)
        analysis_state["report"] = report
        analysis_state["progress"] = 50
        analysis_state["status"] = "Generating predictions..."

        # 3. Predict
        predictions = generate_predictions(report, n_tickets=n_tickets)
        analysis_state["predictions"] = predictions

        if consensus_mode:
            analysis_state["status"] = "Running consensus simulation..."
            analysis_state["progress"] = 70
            consensus = consensus_pick(report, n_tickets=n_tickets)
            analysis_state["consensus"] = consensus

        # 4. Charts
        if include_charts:
            analysis_state["progress"] = 80
            analysis_state["status"] = "Generating charts..."
            generate_all_charts(report)

        analysis_state["progress"] = 100
        analysis_state["status"] = "Complete!"

    except Exception as e:
        analysis_state["status"] = f"Error: {str(e)}"
    finally:
        analysis_state["running"] = False


@app.route("/api/results")
def get_results():
    """Get analysis results"""
    if not analysis_state["report"]:
        return jsonify({"error": "No analysis run yet"}), 400

    report = analysis_state["report"]

    return jsonify({
        "overview": {
            "total_draws": report["total_draws"],
            "date_range": report["date_range"],
            "consecutive_pct": report["consecutive_pct"][0],
            "sum_mean": round(report["sum_stats"]["mean"], 1),
            "sum_std": round(report["sum_stats"]["std"], 1),
            "sum_range": report["sum_stats"]["common_range"],
        },
        "top_numbers": [
            {"number": n, "count": c, "pct": round((c / report["total_draws"]) * 100, 1)}
            for n, c in sorted(report["frequency"].items(), key=lambda x: x[1], reverse=True)[:20]
        ],
        "top_pb": [
            {"number": n, "count": c, "pct": round((c / report["total_draws"]) * 100, 1)}
            for n, c in sorted(report["powerball_frequency"].items(), key=lambda x: x[1], reverse=True)[:10]
        ],
        "hot_numbers": [{"num": n, "freq": c} for n, c in report["hot_numbers"][:15]],
        "cold_numbers": [{"num": n, "freq": c} for n, c in report["cold_numbers"][:15]],
        "overdue": [
            {"num": n, "gap": g, "months": round(g * 3.5 / 30, 1)}
            for n, g in sorted(report["gaps"].items(), key=lambda x: x[1], reverse=True)[:15]
        ],
        "top_pairs": [
            {"pair": f"{a}-{b}", "times": c}
            for (a, b), c in report["top_pairs"][:10]
        ],
        "trends_rising": [
            {"num": n, "trend": round(t * 1000, 1)}
            for n, _, _, t in report["trends"][:10]
        ],
        "trends_falling": [
            {"num": n, "trend": round(t * 1000, 1)}
            for n, _, _, t in report["trends"][-10:][::-1]
        ],
    })


@app.route("/api/predictions")
def get_predictions():
    """Get prediction results"""
    if not analysis_state["predictions"]:
        return jsonify({"error": "No predictions available"}), 400

    predictions = {}
    for strategy, tickets in analysis_state["predictions"].items():
        predictions[strategy] = [
            {
                "numbers": mains,
                "powerball": pb,
                "ticket": f"{' '.join(f'{n:02d}' for n in mains)} | PB: {pb:02d}",
            }
            for mains, pb in tickets
        ]

    result = {"predictions": predictions}

    if analysis_state["consensus"]:
        result["consensus"] = [
            {
                "numbers": mains,
                "powerball": pb,
                "ticket": f"{' '.join(f'{n:02d}' for n in mains)} | PB: {pb:02d}",
            }
            for mains, pb in analysis_state["consensus"]
        ]

    return jsonify(result)


@app.route("/api/charts")
def get_charts():
    """Get list of available charts"""
    charts_dir = "charts"
    if not os.path.exists(charts_dir):
        return jsonify({"charts": []})

    charts = []
    for filename in sorted(os.listdir(charts_dir)):
        if filename.endswith(".png"):
            charts.append({
                "filename": filename,
                "url": f"/charts/{filename}",
                "name": filename.replace("_", " ").replace(".png", "").title(),
            })

    return jsonify({"charts": charts})


@app.route("/charts/<filename>")
def get_chart(filename):
    """Serve chart images"""
    from flask import send_file
    return send_file(f"charts/{filename}", mimetype="image/png")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000, help="Port to run server on")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Powerball Analysis Bot - Web Dashboard")
    print(f"  Open: http://{args.host}:{args.port}")
    print(f"{'='*60}\n")

    app.run(debug=True, host=args.host, port=args.port, use_reloader=False)
