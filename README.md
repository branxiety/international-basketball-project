# How International Players Have Transformed the NBA

**Author:** Brandon Yau · **Course:** DSCI 510 | Final Project

This project quantifies the impact of internationally-born players on the NBA from 2015
through 2024 by combining three sources: a Wikipedia list of internationally-born
NBA players, the Basketball-Reference draft archive, and per-season Advanced
metrics also from Basketball-Reference.

## Repository layout

```
.
├── README.md
├── requirements.txt
├── proposal.pdf
├── data/
│   ├── raw/
│   └── processed/
├── results/
│   ├── final_report.pdf
│   ├── summary_stats.txt
│   └── figures/
└── src/
    ├── scraper.py
    ├── get_data.py
    ├── clean_data.py
    ├── integrate_data.py
    ├── analyze_visualize.py
    └── utils/
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the pipeline

```bash
python src/get_data.py            # raw -> data/raw/
python src/clean_data.py          # cleaned -> data/processed/
python src/integrate_data.py      # joined -> data/processed/
python src/analyze_visualize.py   # figures -> results/figures/
```

## Standalone scraper (Submission 2)

```bash
python src/scraper.py                    # full dataset to stdout
python src/scraper.py --scrape 10        # first 10 rows
python src/scraper.py --save out.csv     # save full dataset
```

## Data sources

| # | Source                                  | Method                  |
|---|-----------------------------------------|-------------------------|
| 1 | Wikipedia: NBA players born outside USA | requests + BeautifulSoup |
| 2 | Basketball-Reference draft pages        | pandas.read_html         |
| 3 | Basketball-Reference advanced stats     | pandas.read_html         |

All three join on a normalized player-name key produced by `clean_data.normalize_name`.
