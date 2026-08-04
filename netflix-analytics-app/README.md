# 🎬 Netflix Content Analytics Dashboard

An interactive data analytics dashboard exploring Netflix's global content
library (8,800+ titles). Built to practice the full analyst workflow: data
cleaning, feature engineering, exploratory analysis, and turning that into
a tool a non-technical person could actually use.

**Live demo:** _[add your Streamlit Cloud link here after deploying]_

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458)

---

## What it does

- Cleans and reshapes the raw Kaggle Netflix dataset (handles missing
  directors/cast/country, splits a mixed "duration" field into
  minutes-for-movies vs. seasons-for-shows, explodes multi-genre and
  multi-country fields for correct counting)
- Interactive filters (content type, release year range, rating)
- KPI summary cards
- Four analysis views: growth over time, genre/rating breakdown, global
  content origin, and a raw data explorer with CSV export
- Dark/light theme toggle
- Every chart tab includes a short written insight, not just the chart

## Why these design choices (for anyone reviewing the code)

- **`src/data_processing.py` is separate from `app.py`** — the cleaning
  and aggregation logic doesn't depend on Streamlit at all, so it could be
  unit tested or reused in a plain Jupyter notebook.
- **Nulls in `director`/`cast`/`country` are filled with `"Unknown"`,
  not dropped.** Director is missing in ~30% of rows — dropping those
  would silently bias the whole dataset toward well-documented titles.
- **`duration` is split into two columns.** It means different things for
  Movies (minutes) vs. TV Shows (seasons); treating it as one field makes
  it impossible to analyze correctly.
- **Genre and country counts use `.explode()`**, because most titles
  belong to 2-3 genres and list multiple co-production countries at once.
  Using the first-listed value only would undercount everything else.

## Tech stack

- **pandas** — cleaning, feature engineering, aggregation
- **Plotly** — interactive charts (bar, line, pie)
- **Streamlit** — UI layer and app framework

## Run it locally

```bash
git clone <your-repo-url>
cd netflix-analytics-app
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
netflix-analytics-app/
├── app.py                  # Streamlit UI, filters, charts, theme toggle
├── src/
│   └── data_processing.py  # Loading, cleaning, feature engineering (no UI code)
├── data/
│   └── netflix_titles.csv  # Kaggle: Netflix Movies and TV Shows
├── requirements.txt
└── README.md
```

## Dataset

[Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
— 8,807 titles, Kaggle.

## Possible extensions

- Sentiment analysis on the `description` field
- Director/cast network analysis
- Predictive model for content rating based on genre + description

---

Built by **Sasikumar Pulluri** —
[Medium](https://medium.com/@sasikumarpulluri) ·
[LinkedIn](https://linkedin.com/in/sasikumar-pulluri-724692341)
