import sys
import csv
import argparse
import requests
import pandas as pd
import time
 
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com",
})
 
draft_years = list(range(2015, 2025))
 
 
def scrape_draft_class(year):
    time.sleep(4)
    url = f"https://www.basketball-reference.com/draft/NBA_{year}.html"
    response = SESSION.get(url, timeout=15)
    print(response.status_code)
    tables = pd.read_html(response.text)
    for i, table in enumerate(tables):
        print(f"Table {i}: {list(table.columns)}")
 
    # the main draft table has a "WS" column
    for table in tables:
        table.columns = [col[-1] for col in table.columns]
        if "WS" in table.columns and "VORP" in table.columns:
            df = table.copy()
            # drop repeated header rows
            df = df[df["Pk"] != "Pk"]
            # keep only the columns we need
            df = df[["Pk", "Player", "WS", "VORP"]].copy()
            df["draft_year"] = year
            df = df.dropna(subset=["Player"])
            df = df[df["Player"] != "Player"]
            return df
 
    return pd.DataFrame()
 
 
def scrape_all(limit=None):
    all_rows = []
    for year in draft_years:
        df = scrape_draft_class(year)
        for _, row in df.iterrows():
            all_rows.append({
                "draft_year": row["draft_year"],
                "pick": row["Pk"],
                "player_name": row["Player"],
                "ws": row["WS"],
                "vorp": row["VORP"],
            })
            if limit and len(all_rows) >= limit:
                return all_rows
    return all_rows
 
 
def print_rows(rows):
    writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
 
 
def save_rows(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {path}", file=sys.stderr)
 
 
parser = argparse.ArgumentParser()
parser.add_argument("--scrape", type=int)
parser.add_argument("--save", default="/Users/brandonyau/USC/DSCI-510/project/data.csv", type=str)
args = parser.parse_args()
 
if args.scrape:
    print_rows(scrape_all(limit=args.scrape))
elif args.save:
    save_rows(scrape_all(), args.save)
else:
    print_rows(scrape_all())