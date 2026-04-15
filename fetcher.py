"""
Fetches historical Powerball data from the official lottery data source.
Uses powerball.com's historical results endpoint.
"""

import requests
import csv
import os
import json
import time
from datetime import datetime

DATA_FILE = "powerball_history.csv"
API_URL = "https://www.powerball.com/api/v1/drawings/powerball"


def fetch_from_powerball_api(max_pages=100):
    """Fetch historical draws from powerball.com paginated API."""
    all_draws = []
    page = 1
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    print(f"[fetcher] Fetching Powerball history from powerball.com API...")

    while page <= max_pages:
        url = f"{API_URL}?page={page}&itemsPerPage=20&startDate=2004-01-01"
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"[fetcher] API returned {resp.status_code} on page {page}, stopping.")
                break
            data = resp.json()
            # API returns a list of draw objects
            draws = data.get("data", data) if isinstance(data, dict) else data
            if not draws:
                break
            for draw in draws:
                all_draws.append(parse_api_draw(draw))
            print(f"[fetcher] Page {page}: got {len(draws)} draws (total so far: {len(all_draws)})")
            if len(draws) < 20:
                break
            page += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"[fetcher] Error on page {page}: {e}")
            break

    return [d for d in all_draws if d is not None]


def parse_api_draw(draw):
    """Parse a single draw record from the API."""
    try:
        # Different possible field names depending on API version
        date_str = draw.get("field_draw_date") or draw.get("draw_date") or draw.get("date", "")
        numbers_raw = draw.get("field_winning_numbers") or draw.get("winning_numbers") or ""
        powerball_raw = draw.get("field_powerball") or draw.get("powerball") or ""
        multiplier_raw = draw.get("field_multiplier") or draw.get("multiplier") or ""

        # Normalize date
        date = ""
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"]:
            try:
                date = datetime.strptime(str(date_str)[:10], fmt[:len(fmt)]).strftime("%Y-%m-%d")
                break
            except Exception:
                continue

        # Normalize numbers
        if isinstance(numbers_raw, list):
            numbers = [int(n) for n in numbers_raw]
        else:
            numbers = [int(n.strip()) for n in str(numbers_raw).replace(",", " ").split() if n.strip().isdigit()]

        powerball = int(str(powerball_raw).strip()) if str(powerball_raw).strip().isdigit() else None
        multiplier = str(multiplier_raw).strip() if multiplier_raw else ""

        if len(numbers) == 5 and powerball:
            return {
                "date": date,
                "n1": numbers[0],
                "n2": numbers[1],
                "n3": numbers[2],
                "n4": numbers[3],
                "n5": numbers[4],
                "powerball": powerball,
                "multiplier": multiplier,
            }
    except Exception:
        pass
    return None


def fetch_from_csv_backup():
    """
    Fetch from a well-known public CSV dataset of Powerball results.
    Falls back to a hardcoded URL for the NY Open Data / lottery dataset.
    """
    # This is a public Powerball dataset hosted on GitHub
    url = (
        "https://raw.githubusercontent.com/"
        "zonination/powerball/master/powerball.csv"
    )
    print(f"[fetcher] Trying backup CSV source...")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            lines = resp.text.strip().split("\n")
            draws = []
            reader = csv.DictReader(lines)
            for row in reader:
                draws.append(parse_csv_row(row))
            result = [d for d in draws if d is not None]
            print(f"[fetcher] Backup source: got {len(result)} draws.")
            return result
    except Exception as e:
        print(f"[fetcher] Backup source failed: {e}")
    return []


def parse_csv_row(row):
    """Parse a CSV row — handles multiple common column formats."""
    try:
        # Try to find date
        date_val = (
            row.get("Draw Date")
            or row.get("date")
            or row.get("DrawDate")
            or row.get("Date", "")
        )
        date = ""
        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"]:
            try:
                date = datetime.strptime(str(date_val).strip(), fmt).strftime("%Y-%m-%d")
                break
            except Exception:
                continue

        # Try to find numbers
        nums = []
        for key in ["Winning Numbers", "winning_numbers", "numbers", "Numbers"]:
            if key in row and row[key]:
                raw = str(row[key]).strip()
                nums = [int(n) for n in raw.replace(",", " ").split() if n.strip().isdigit()]
                if len(nums) >= 5:
                    break

        # Try individual number columns
        if len(nums) < 5:
            for i in range(1, 6):
                for key in [f"Number {i}", f"n{i}", f"Num{i}", f"Ball{i}"]:
                    if key in row and row[key]:
                        try:
                            nums.append(int(row[key].strip()))
                            break
                        except Exception:
                            pass

        # Powerball
        pb = None
        for key in ["Powerball", "powerball", "PB", "Mega Ball"]:
            if key in row and row[key]:
                try:
                    pb = int(str(row[key]).strip())
                    break
                except Exception:
                    pass

        multiplier = row.get("Multiplier", row.get("Power Play", "")).strip()

        if len(nums) >= 5 and pb:
            return {
                "date": date,
                "n1": nums[0],
                "n2": nums[1],
                "n3": nums[2],
                "n4": nums[3],
                "n5": nums[4],
                "powerball": pb,
                "multiplier": multiplier,
            }
    except Exception:
        pass
    return None


def save_to_csv(draws, filepath=DATA_FILE):
    """Save draw records to a local CSV file."""
    if not draws:
        return
    fieldnames = ["date", "n1", "n2", "n3", "n4", "n5", "powerball", "multiplier"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(draws)
    print(f"[fetcher] Saved {len(draws)} draws to {filepath}")


def load_from_csv(filepath=DATA_FILE):
    """Load draw records from a local CSV file."""
    draws = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                draws.append({
                    "date": row["date"],
                    "n1": int(row["n1"]),
                    "n2": int(row["n2"]),
                    "n3": int(row["n3"]),
                    "n4": int(row["n4"]),
                    "n5": int(row["n5"]),
                    "powerball": int(row["powerball"]),
                    "multiplier": row.get("multiplier", ""),
                })
            except Exception:
                continue
    return draws


def get_data(force_refresh=False):
    """
    Main entry point: returns list of draw dicts.
    Uses cached CSV if available, otherwise fetches fresh data.
    Falls back to synthetic data if online sources fail.
    """
    if not force_refresh and os.path.exists(DATA_FILE):
        print(f"[fetcher] Loading cached data from {DATA_FILE}")
        draws = load_from_csv()
        print(f"[fetcher] Loaded {len(draws)} draws from cache.")
        return draws

    # Try live API first
    draws = fetch_from_powerball_api()

    # If API fails or returns too few, try backup CSV
    if len(draws) < 100:
        backup = fetch_from_csv_backup()
        if len(backup) > len(draws):
            draws = backup

    # If still no data, generate synthetic dataset
    if len(draws) < 100:
        print("[fetcher] No online data available. Generating synthetic dataset...")
        try:
            from synthetic_data_generator import generate_synthetic_draws
            draws = generate_synthetic_draws()
            print(f"[fetcher] Generated {len(draws)} synthetic draws for analysis.")
        except Exception as e:
            print(f"[fetcher] ERROR: Could not generate synthetic data: {e}")
            return []

    if draws:
        # Sort by date ascending
        draws = sorted(draws, key=lambda d: d["date"])
        save_to_csv(draws)
    else:
        print("[fetcher] ERROR: Could not obtain any data.")

    return draws
