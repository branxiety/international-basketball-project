"""Clean and normalize the three raw files. Writes data/processed/*.csv."""

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent / "data"
RAW, PROC = BASE / "raw", BASE / "processed"
PROC.mkdir(parents=True, exist_ok=True)


def normalize_name(raw):
    if not isinstance(raw, str):
        return ""
    s = unicodedata.normalize("NFKD", raw)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    tokens = [t for t in s.split() if t not in ("jr", "sr", "ii", "iii", "iv")]
    return " ".join(tokens)


def main():
    # Wikipedia
    wiki = pd.read_csv(RAW / "wikipedia_internationals.csv")
    wiki["player_key"] = wiki["player_name"].map(normalize_name)
    wiki = wiki[wiki["player_key"] != ""].drop_duplicates("player_key")
    wiki[["player_key", "player_name", "country"]].to_csv(
        PROC / "wikipedia_clean.csv", index=False)
    print(f"wikipedia: {len(wiki)} players", file=sys.stderr)

    # Drafts
    drafts = pd.read_csv(RAW / "draft_picks.csv")
    drafts["player_key"] = drafts["player_name"].map(normalize_name)
    for col in ("pick", "ws", "vorp", "draft_year"):
        drafts[col] = pd.to_numeric(drafts[col], errors="coerce")
    drafts = drafts.dropna(subset=["pick", "player_key"])
    drafts[["ws", "vorp"]] = drafts[["ws", "vorp"]].fillna(0)
    drafts["pick"] = drafts["pick"].astype(int)
    drafts["draft_year"] = drafts["draft_year"].astype(int)
    drafts = drafts.drop_duplicates(["draft_year", "pick"])
    drafts[["player_key", "player_name", "draft_year", "pick", "ws", "vorp"]].to_csv(
        PROC / "drafts_clean.csv", index=False)
    print(f"drafts: {len(drafts)} picks", file=sys.stderr)

    # Advanced stats
    adv = pd.read_csv(RAW / "advanced_stats.csv")
    adv["player_key"] = adv["player_name"].map(normalize_name)
    adv = adv[adv["player_key"] != ""]
    adv = adv.dropna(subset=["minutes"])
    adv = adv[adv["minutes"] > 0]
    adv = adv.drop_duplicates(["player_key", "season"])
    adv.to_csv(PROC / "advanced_clean.csv", index=False)
    print(f"advanced: {len(adv)} player-seasons", file=sys.stderr)


if __name__ == "__main__":
    main()
