"""Join the three cleaned tables on player_key. Writes data/processed/*.csv."""

import sys
from pathlib import Path

import pandas as pd

PROC = Path(__file__).resolve().parent.parent / "data" / "processed"

wiki = pd.read_csv(PROC / "wikipedia_clean.csv")[["player_key", "country"]]
drafts = pd.read_csv(PROC / "drafts_clean.csv")
adv = pd.read_csv(PROC / "advanced_clean.csv")

# A player is international if they appear in the Wikipedia list
players = drafts.merge(wiki, on="player_key", how="left")
players["is_international"] = players["country"].notna()
players["country"] = players["country"].fillna("United States")
players.to_csv(PROC / "players_integrated.csv", index=False)
print(f"players_integrated: {len(players)} rows "
      f"({players['is_international'].sum()} international)", file=sys.stderr)

seasons = adv.merge(wiki, on="player_key", how="left")
seasons["is_international"] = seasons["country"].notna()
seasons["country"] = seasons["country"].fillna("United States")
seasons.to_csv(PROC / "seasons_integrated.csv", index=False)
print(f"seasons_integrated: {len(seasons)} rows "
      f"({seasons['is_international'].sum()} international)", file=sys.stderr)
