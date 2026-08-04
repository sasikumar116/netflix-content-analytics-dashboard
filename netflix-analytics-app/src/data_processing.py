"""
data_processing.py
-------------------
Handles loading, cleaning, and feature engineering for the Netflix
Movies & TV Shows dataset.

Keeping this separate from the UI (app.py) is intentional: it means
the analysis logic can be unit-tested, reused in a notebook, or run
from the command line -- independent of Streamlit.
"""

import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def load_data(path: str = "data/netflix_titles.csv") -> pd.DataFrame:
    """Load the raw CSV. Cached so Streamlit doesn't re-read the file
    on every widget interaction (a common beginner mistake that makes
    Streamlit apps feel slow)."""
    df = pd.read_csv(path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw Netflix dataset and engineers analysis-ready columns.

    Design decisions (worth remembering for interviews):
    - director/cast/country nulls are filled with 'Unknown' rather than
      dropped, because dropping would remove ~30% of rows (director is
      missing in 2,634 of 8,807 rows) and bias the dataset toward
      well-documented titles.
    - date_added nulls (10 rows) ARE dropped, since that's <0.2% of data
      and there's no reasonable way to impute a missing add-date.
    - duration is split into two separate numeric columns because it
      means two different things depending on `type` (minutes for
      Movies, seasons for TV Shows) -- keeping it as one mixed field
      makes it impossible to analyze correctly.
    """
    df = df.copy()

    # Fill categorical nulls with an explicit label instead of dropping rows
    for col in ["director", "cast", "country"]:
        df[col] = df[col].fillna("Unknown")

    df["rating"] = df["rating"].fillna(df["rating"].mode()[0])

    # Drop the tiny number of rows with no date_added or duration (unrecoverable)
    df = df.dropna(subset=["date_added", "duration"])

    # Parse date_added into a real datetime, then derive year/month
    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), format="%B %d, %Y")
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month_name()

    # Split duration into type-specific numeric columns
    df["duration_minutes"] = np.where(
        df["type"] == "Movie",
        df["duration"].str.extract(r"(\d+)").astype(float)[0],
        np.nan,
    )
    df["duration_seasons"] = np.where(
        df["type"] == "TV Show",
        df["duration"].str.extract(r"(\d+)").astype(float)[0],
        np.nan,
    )

    # Primary country: many titles list several co-production countries
    # (e.g. "United States, Ghana, Burkina Faso"). For country-level
    # aggregation we take the first listed as the primary market.
    df["primary_country"] = df["country"].apply(lambda x: x.split(",")[0].strip())

    # Primary genre, same logic as country
    df["primary_genre"] = df["listed_in"].apply(lambda x: x.split(",")[0].strip())

    # Content age at the time it was added to Netflix -- a proxy for
    # "how much licensed/back-catalog content vs. fresh content"
    df["content_age_when_added"] = df["year_added"] - df["release_year"]
    # A handful of rows have negative content age (data entry errors where
    # release_year postdates date_added) -- clip at 0 rather than drop them
    df["content_age_when_added"] = df["content_age_when_added"].clip(lower=0)

    return df


def get_genre_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Explode the comma-separated `listed_in` column into one row per
    (title, genre) pair, then count. Needed because ~all titles belong
    to 2-3 genres simultaneously -- primary_genre alone undercounts."""
    genres = df["listed_in"].str.split(", ").explode()
    counts = genres.value_counts()
    return pd.DataFrame({"genre": counts.index, "count": counts.values})


def get_country_counts(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Same explode logic for country, since co-productions list multiple."""
    countries = df["country"].str.split(", ").explode()
    countries = countries[countries != "Unknown"]
    counts = countries.value_counts().head(top_n)
    return pd.DataFrame({"country": counts.index, "count": counts.values})


def kpi_summary(df: pd.DataFrame) -> dict:
    """Top-line KPIs shown in the dashboard header cards."""
    return {
        "total_titles": len(df),
        "movies": int((df["type"] == "Movie").sum()),
        "tv_shows": int((df["type"] == "TV Show").sum()),
        "countries": df["country"].str.split(", ").explode().nunique(),
        "avg_movie_duration": round(df["duration_minutes"].mean(), 1),
        "avg_tv_seasons": round(df["duration_seasons"].mean(), 1),
        "date_range": (int(df["release_year"].min()), int(df["release_year"].max())),
    }
