"""Pull raw data from all three sources into data/raw/."""

import sys
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

YEARS = list(range(2015, 2025))
HEADERS = {"User-Agent": "Mozilla/5.0"}


# Source 1: Wikipedia

def get_wikipedia():
    url = ("https://en.wikipedia.org/wiki/"
           "List_of_NBA_players_born_outside_the_United_States")
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")

    # The roster is one big sortable wikitable: columns are
    # Nationality | Birthplace | Player | Pos. | Career | Yrs | Notes | Ref.
    rows = []
    for table in soup.select("table.wikitable"):
        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        if not headers:
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if not any("Nationality" in h for h in headers):
            continue
        if not any("Player" in h for h in headers):
            continue

        # find the column indices we care about
        nat_idx = next(i for i, h in enumerate(headers) if "Nationality" in h)
        ply_idx = next(i for i, h in enumerate(headers) if "Player" in h)

        for tr in table.select("tbody tr"):
            cells = tr.find_all(["td", "th"])
            if len(cells) <= max(nat_idx, ply_idx):
                continue
            country = cells[nat_idx].get_text(strip=True).split("[")[0]
            # the player cell usually wraps the name in an <a>
            link = cells[ply_idx].find("a")
            name = (link.get_text(strip=True) if link
                    else cells[ply_idx].get_text(strip=True))
            name = name.split("[")[0].strip()
            if name and country:
                rows.append({"player_name": name, "country": country})

    return pd.DataFrame(rows).drop_duplicates()


# Source 2: Basketball-Reference draft pages

def get_drafts():
    rows = []
    for year in YEARS:
        url = f"https://www.basketball-reference.com/draft/NBA_{year}.html"
        resp = requests.get(url, headers=HEADERS)
        resp.encoding = "utf-8"
        for table in pd.read_html(resp.text):
            table.columns = [c[-1] if isinstance(c, tuple) else c
                             for c in table.columns]
            if {"Pk", "Player", "WS", "VORP"}.issubset(table.columns):
                df = table[table["Pk"] != "Pk"].dropna(subset=["Player"])
                df = df[df["Player"] != "Player"]
                df = df[["Pk", "Player", "WS", "VORP"]].copy()
                df.columns = ["pick", "player_name", "ws", "vorp"]
                df["draft_year"] = year
                rows.append(df)
                break
        time.sleep(3.5)
    return pd.concat(rows, ignore_index=True)


# Source 3: Basketball-Reference advanced stats by season

def get_advanced():
    rows = []
    for year in YEARS:
        url = f"https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html"
        resp = requests.get(url, headers=HEADERS)
        resp.encoding = "utf-8"
        for table in pd.read_html(resp.text):
            if {"PER", "TS%", "USG%", "VORP"}.issubset(table.columns):
                df = table[table["Player"] != "Player"].dropna(subset=["Player"])
                rows.append(pd.DataFrame({
                    "player_name": df["Player"],
                    "season": year,
                    "games": pd.to_numeric(df["G"], errors="coerce"),
                    "minutes": pd.to_numeric(df["MP"], errors="coerce"),
                    "per": pd.to_numeric(df["PER"], errors="coerce"),
                    "ts_pct": pd.to_numeric(df["TS%"], errors="coerce"),
                    "usg_pct": pd.to_numeric(df["USG%"], errors="coerce"),
                    "bpm": pd.to_numeric(df["BPM"], errors="coerce"),
                    "vorp": pd.to_numeric(df["VORP"], errors="coerce"),
                }))
                break
        time.sleep(3.5)
    return pd.concat(rows, ignore_index=True)


if __name__ == "__main__":
    for name, fn in [("wikipedia_internationals", get_wikipedia),
                     ("draft_picks", get_drafts),
                     ("advanced_stats", get_advanced)]:
        print(f"fetching {name}...", file=sys.stderr)
        df = fn()
        out = RAW_DIR / f"{name}.csv"
        df.to_csv(out, index=False, encoding="utf-8")
        print(f"  wrote {len(df)} rows -> {out}", file=sys.stderr)
