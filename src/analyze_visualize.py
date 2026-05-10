"""Produce the figures and summary numbers used in the final report."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"
FIG = BASE / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

players = pd.read_csv(PROC / "players_integrated.csv")
seasons = pd.read_csv(PROC / "seasons_integrated.csv")
intl = players[players["is_international"]]
dom = players[~players["is_international"]]

DOM_COLOR, INT_COLOR = "#1d428a", "#c8102e"   # NBA blue and red


# Figure 1: top contributing countries

counts = intl["country"].value_counts().head(10)
counts.plot(kind="bar")
plt.ylabel("Players drafted (2015-2024)")
plt.title("Top countries by NBA players drafted, 2015-2024")
plt.tight_layout()
plt.savefig(FIG / "fig1_country_counts.png")
plt.close()


# Figure 2: international share of league minutes by season

share = seasons.groupby(["season", "is_international"])["minutes"].sum().unstack()
intl_pct = 100 * share[True] / (share[True] + share[False])
intl_pct.plot(marker="o")
plt.xlabel("Season (ending year)")
plt.ylabel("% of league minutes")
plt.title("International share of NBA minutes, 2015-2024")
plt.tight_layout()
plt.savefig(FIG / "fig2_share_by_year.png")
plt.close()


# Figure 3: pick vs. career WS, by group

for label, group, color in [("Domestic", dom, DOM_COLOR),
                             ("International", intl, INT_COLOR)]:
    plt.scatter(group["pick"], group["ws"], color=color, alpha=0.4, label=label)
    m, b = np.polyfit(np.log(group["pick"]), group["ws"], 1)
    xs = np.linspace(1, group["pick"].max(), 100)
    plt.plot(xs, m * np.log(xs) + b, color=color)
plt.xlabel("Draft pick (1 = first overall)")
plt.ylabel("Career Win Shares")
plt.title("Draft pick vs. career Win Shares, 2015-2024")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "fig3_pick_vs_career_ws.png")
plt.close()


# Figure 4: mean career WS by pick range, by group

buckets = [(1, 5, "1-5"), (6, 14, "6-14"), (15, 30, "15-30"), (31, 60, "31-60")]
rows = []
for lo, hi, label in buckets:
    chunk = players[(players["pick"] >= lo) & (players["pick"] <= hi)]
    rows.append({
        "Domestic": chunk[~chunk["is_international"]]["ws"].mean(),
        "International": chunk[chunk["is_international"]]["ws"].mean(),
    })
bucket_df = pd.DataFrame(rows, index=[b[2] for b in buckets])
bucket_df.plot(kind="bar", color=[DOM_COLOR, INT_COLOR])
plt.xlabel("Draft pick range")
plt.ylabel("Mean career Win Shares")
plt.title("Career value per pick range, domestic vs. international")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(FIG / "fig4_value_per_pick.png")
plt.close()


# Figure 5: style metrics by group over time

trend = seasons.groupby(["season", "is_international"])[
    ["ts_pct", "usg_pct", "per"]].mean().reset_index()
trend["group"] = trend["is_international"].map({True: "International", False: "Domestic"})

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
for ax, metric, title in zip(axes,
                              ["ts_pct", "usg_pct", "per"],
                              ["True Shooting %", "Usage %", "PER"]):
    for grp, color in [("Domestic", DOM_COLOR), ("International", INT_COLOR)]:
        sub = trend[trend["group"] == grp]
        ax.plot(sub["season"], sub[metric], marker="o", color=color, label=grp)
    ax.set_title(title)
    ax.set_xlabel("Season")
axes[0].legend()
plt.tight_layout()
plt.savefig(FIG / "fig5_style_metrics.png")
plt.close()


# Summary numbers for the report

with open(BASE / "results" / "summary_stats.txt", "w") as f:
    f.write(f"total picks: {len(players)}\n")
    f.write(f"intl picks:  {len(intl)} ({100*len(intl)/len(players):.1f}%)\n")
    f.write(f"mean career WS, domestic:      {dom['ws'].mean():.2f}\n")
    f.write(f"mean career WS, international: {intl['ws'].mean():.2f}\n")
    f.write(f"median pick, domestic:      {dom['pick'].median():.0f}\n")
    f.write(f"median pick, international: {intl['pick'].median():.0f}\n")
    f.write(f"intl share of minutes, {intl_pct.index.min()}: {intl_pct.iloc[0]:.1f}%\n")
    f.write(f"intl share of minutes, {intl_pct.index.max()}: {intl_pct.iloc[-1]:.1f}%\n")
    f.write("\ntop countries:\n")
    for c, n in counts.items():
        f.write(f"  {c}: {n}\n")
    f.write("\nvalue per pick bucket:\n")
    for label, row in bucket_df.iterrows():
        f.write(f"  {label}: dom={row['Domestic']:.2f}, "
                f"intl={row['International']:.2f}\n")

print("wrote 5 figures + summary_stats.txt", file=sys.stderr)