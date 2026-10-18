#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint and write data/contributions.json with raw days plus derived stats.
"""
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "sandeepmegharaj")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("no calendar cells found -- checking table cells", file=sys.stderr)
        cells = soup.select("td[data-date]")

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        if not text:
            # fallback to td text or aria-label
            text = td.get("aria-label", "") or td.get_text(strip=True)
            
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0
        days.append({"date": date, "count": count, "level": int(td.get("data-level") or 0)})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

    # streaks
    cur_streak = {"length": 0, "start": "", "end": ""}
    longest_streak = {"length": 0, "start": "", "end": ""}

    run = 0
    run_start = ""
    for d in days:
        if d["count"] > 0:
            if run == 0:
                run_start = d["date"]
            run += 1
            if run > longest_streak["length"]:
                longest_streak = {"length": run, "start": run_start, "end": d["date"]}
        else:
            run = 0

    # current streak from end
    run = 0
    for d in reversed(days):
        if d["count"] > 0:
            if run == 0:
                cur_streak["end"] = d["date"]
            run += 1
            cur_streak["start"] = d["date"]
        else:
            if run > 0:
                break
    cur_streak["length"] = run

    # monthly breakdown
    months = {}
    for d in days:
        m_key = d["date"][:7]
        months[m_key] = months.get(m_key, 0) + d["count"]

    return {
        "user": USERNAME,
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "best_day": best,
        "current_streak": cur_streak,
        "longest_streak": longest_streak,
        "monthly": months,
        "days": days,
    }


def main():
    print(f"Fetching contributions for {USERNAME}...")
    days = fetch_days()
    print(f"Found {len(days)} days.")
    stats = compute_stats(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Saved stats to {OUT_PATH} (Total: {stats['total_contributions']})")


if __name__ == "__main__":
    main()
