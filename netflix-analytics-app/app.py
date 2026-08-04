"""
app.py
------
Netflix Content Analytics Dashboard
Author: Sasikumar Pulluri

An interactive Streamlit dashboard analyzing Netflix's global content
library (8,800+ titles) -- content mix, growth over time, genre and
country distribution, and rating breakdown. Built as a data analyst
portfolio project: pandas for transformation, Plotly for interactive
charts, Streamlit for the UI layer.

Run locally:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing import (
    load_data,
    clean_data,
    get_genre_counts,
    get_country_counts,
    kpi_summary,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Netflix Content Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Netflix Theme — custom CSS only for our own components.
# The base dark theme (black bg, red accent, white text) is set in
# .streamlit/config.toml so that built-in widgets (dataframes, inputs)
# render correctly without interference.
# ---------------------------------------------------------------------------
NETFLIX_BLACK   = "#000000"
NETFLIX_DARK    = "#141414"
NETFLIX_CARD    = "#1a1a1a"
NETFLIX_BORDER  = "#2a2a2a"
NETFLIX_RED     = "#e50914"
NETFLIX_WHITE   = "#f5f5f5"
NETFLIX_GREY    = "#808080"
PLOTLY_TEMPLATE = "plotly_dark"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }}

    /* ── KPI CARDS ─────────────────────────────────── */
    .kpi-card {{
        background-color: {NETFLIX_CARD};
        border: 1px solid {NETFLIX_BORDER};
        border-radius: 8px;
        padding: 20px 22px;
        text-align: left;
        transition: border-color 0.2s ease;
    }}
    .kpi-card:hover {{ border-color: {NETFLIX_RED}; }}
    .kpi-value {{
        font-size: 30px;
        font-weight: 800;
        color: {NETFLIX_WHITE};
        line-height: 1.1;
        letter-spacing: -0.5px;
    }}
    .kpi-label {{
        font-size: 11px;
        color: {NETFLIX_GREY};
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
    }}

    /* ── ACTIVE TAB UNDERLINE ───────────────────────── */
    [data-testid="stTab"][aria-selected="true"] {{
        border-bottom: 3px solid {NETFLIX_RED} !important;
    }}

    /* ── SCROLLBAR ──────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {NETFLIX_DARK}; }}
    ::-webkit-scrollbar-thumb {{ background: {NETFLIX_BORDER}; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {NETFLIX_GREY}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar — branding + filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎬 Netflix Analytics")
    st.caption("Data Analyst Portfolio Project by Sasikumar Pulluri")
    st.divider()
    st.markdown("**Filters**")

# ---------------------------------------------------------------------------
# Load + clean data
# ---------------------------------------------------------------------------
raw_df = load_data()
df = clean_data(raw_df)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    type_filter = st.multiselect(
        "Content Type", options=sorted(df["type"].unique()), default=list(df["type"].unique())
    )
    year_min, year_max = int(df["release_year"].min()), int(df["release_year"].max())
    year_range = st.slider(
        "Release Year Range", min_value=year_min, max_value=year_max,
        value=(2000, year_max),
    )
    rating_filter = st.multiselect(
        "Rating", options=sorted(df["rating"].unique()), default=list(df["rating"].unique())
    )

    st.divider()
    st.caption("Data: Kaggle 'Netflix Movies and TV Shows' (8,807 titles)")
    st.caption("[GitHub](https://github.com) · [Medium](https://medium.com/@sasikumarpulluri)")

filtered = df[
    (df["type"].isin(type_filter))
    & (df["release_year"].between(*year_range))
    & (df["rating"].isin(rating_filter))
]

if filtered.empty:
    st.warning("No titles match the current filters. Try widening your selection.")
    st.stop()

# ---------------------------------------------------------------------------
# Header + KPI cards
# ---------------------------------------------------------------------------
# Netflix-style red underline on title
st.markdown(
    f"""
    <h1 style="font-size:2.2rem;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;">
        <span style="color:{NETFLIX_RED};">Netflix</span> Content Analytics Dashboard
    </h1>
    """,
    unsafe_allow_html=True,
)
st.caption(
    f"Analyzing {len(filtered):,} titles "
    f"({year_range[0]}–{year_range[1]}) · Built with pandas + Plotly + Streamlit"
)

kpis = kpi_summary(filtered)

kpi_cols = st.columns(5)
kpi_data = [
    ("Total Titles", f"{kpis['total_titles']:,}"),
    ("Movies", f"{kpis['movies']:,}"),
    ("TV Shows", f"{kpis['tv_shows']:,}"),
    ("Countries", f"{kpis['countries']}"),
    ("Avg Movie Length", f"{kpis['avg_movie_duration']} min"),
]
for col, (label, value) in zip(kpi_cols, kpi_data):
    with col:
        st.markdown(
            f"""<div class="kpi-card">
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-label">{label}</div>
                </div>""",
            unsafe_allow_html=True,
        )

st.write("")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📈 Growth Over Time", "🎭 Genres & Ratings", "🌍 Global Reach", "🔎 Explore Data",
     "🏆 Best Rated", "🌐 Top 10 by Country"]
)

# Shared Plotly layout overrides for Netflix black background
PLOTLY_LAYOUT = dict(
    paper_bgcolor=NETFLIX_DARK,
    plot_bgcolor=NETFLIX_DARK,
    font=dict(color=NETFLIX_WHITE, family="Inter, Helvetica Neue, Arial, sans-serif"),
    title_font=dict(color=NETFLIX_WHITE, size=16, family="Inter, Helvetica Neue, Arial, sans-serif"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=NETFLIX_WHITE)),
    xaxis=dict(gridcolor=NETFLIX_BORDER, zerolinecolor=NETFLIX_BORDER, color=NETFLIX_WHITE),
    yaxis=dict(gridcolor=NETFLIX_BORDER, zerolinecolor=NETFLIX_BORDER, color=NETFLIX_WHITE),
)

# --- Tab 1: Growth over time -------------------------------------------------
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        yearly = filtered.groupby(["year_added", "type"]).size().reset_index(name="count")
        fig = px.line(
            yearly, x="year_added", y="count", color="type",
            markers=True, template=PLOTLY_TEMPLATE,
            color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#b3b3b3"},
            title="Titles Added to Netflix by Year",
        )
        fig.update_layout(legend_title_text="", xaxis_title="Year Added", yaxis_title="Titles Added", **PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        type_counts_raw = filtered["type"].value_counts()
        type_counts = pd.DataFrame({"type": type_counts_raw.index, "count": type_counts_raw.values})
        fig2 = px.pie(
            type_counts, names="type", values="count", hole=0.55,
            template=PLOTLY_TEMPLATE, color="type",
            color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#444444"},
            title="Movie vs TV Show Split",
        )
        fig2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### 💡 Insight")
    peak_year = int(yearly.groupby("year_added")["count"].sum().idxmax())
    st.info(
        f"Content additions peaked in **{peak_year}**, reflecting Netflix's aggressive "
        f"library expansion before the platform matured. Movies consistently outnumber "
        f"TV shows roughly **{kpis['movies']//max(kpis['tv_shows'],1)}:1** in this filtered view, "
        f"suggesting movies are the faster, cheaper way to keep the catalog growing."
    )

# --- Tab 2: Genres & Ratings --------------------------------------------------
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        genre_counts = get_genre_counts(filtered).head(10)
        fig3 = px.bar(
            genre_counts.sort_values("count"), x="count", y="genre", orientation="h",
            template=PLOTLY_TEMPLATE, color_discrete_sequence=[NETFLIX_RED],
            title="Top 10 Genres by Title Count",
        )
        fig3.update_layout(yaxis_title="", xaxis_title="Number of Titles", **PLOTLY_LAYOUT)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        rating_counts_raw = filtered["rating"].value_counts()
        rating_counts = pd.DataFrame({"rating": rating_counts_raw.index, "count": rating_counts_raw.values})
        fig4 = px.bar(
            rating_counts, x="rating", y="count",
            template=PLOTLY_TEMPLATE, color_discrete_sequence=[NETFLIX_RED],
            title="Content Rating Distribution",
        )
        fig4.update_layout(xaxis_title="Rating", yaxis_title="Number of Titles", **PLOTLY_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("##### 💡 Insight")
    top_genre = genre_counts.iloc[0]["genre"]
    top_rating = rating_counts.iloc[0]["rating"]
    st.info(
        f"**{top_genre}** is the single most common genre tag in this filtered view. "
        f"**{top_rating}** is the most frequent content rating, which tells you a lot about "
        f"who Netflix's core content strategy actually targets -- worth cross-checking "
        f"against subscriber demographics if this were a real business analysis."
    )

# --- Tab 3: Global reach -------------------------------------------------------
with tab3:
    country_counts = get_country_counts(filtered, top_n=15)

    fig5 = px.bar(
        country_counts.sort_values("count"), x="count", y="country", orientation="h",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=[NETFLIX_RED],
        title="Top 15 Content-Producing Countries",
    )
    fig5.update_layout(yaxis_title="", xaxis_title="Number of Titles", **PLOTLY_LAYOUT)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("##### 💡 Insight")
    top_country = country_counts.iloc[0]["country"]
    top_country_pct = round(country_counts.iloc[0]["count"] / len(filtered) * 100, 1)
    st.info(
        f"**{top_country}** dominates content origin, appearing in roughly "
        f"**{top_country_pct}%** of titles in this filtered view (note: titles can list "
        f"multiple co-production countries, so percentages across countries won't sum to 100%)."
    )

# --- Tab 4: Raw data explorer ---------------------------------------------------
with tab4:
    st.markdown("Use the filters in the sidebar, then browse or export the filtered dataset.")
    display_cols = [
        "title", "type", "primary_genre", "primary_country",
        "release_year", "rating", "duration", "year_added",
    ]
    # Fixed sequential serial numbers starting from 1
    explore_df = filtered[display_cols].sort_values("year_added", ascending=False).reset_index(drop=True)
    explore_df.index = explore_df.index + 1
    explore_df.index.name = "S.No"
    st.dataframe(explore_df, use_container_width=True, height=450)

    csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download filtered data as CSV", data=csv,
        file_name="netflix_filtered.csv", mime="text/csv",
    )

# --- Tab 5: Best Rated Movies & TV Shows ----------------------------------------
with tab5:
    st.markdown("### 🏆 Best Movies & TV Shows")
    st.caption(
        "Ranked by content maturity rating tier and recency. "
        "Tier 1 (premium mature content) → Tier 6 (unrated)."
    )

    rating_tier = {
        "TV-MA": 1, "R": 1, "NC-17": 1,
        "TV-14": 2, "PG-13": 2,
        "TV-PG": 3, "PG": 3,
        "TV-G": 4, "G": 4,
        "TV-Y7": 5, "TV-Y7-FV": 5, "TV-Y": 5,
        "NR": 6, "UR": 6,
    }
    filtered_ranked = filtered.copy()
    filtered_ranked["rating_tier"] = filtered_ranked["rating"].map(rating_tier).fillna(6)

    best_cols = ["title", "primary_genre", "primary_country", "release_year", "rating", "duration"]

    col_m, col_t = st.columns(2)

    with col_m:
        st.markdown("#### 🎬 Top 25 Movies")
        best_movies = (
            filtered_ranked[filtered_ranked["type"] == "Movie"]
            .sort_values(["rating_tier", "release_year"], ascending=[True, False])
            .head(25)
            [best_cols]
            .reset_index(drop=True)
        )
        best_movies.index = best_movies.index + 1
        best_movies.index.name = "Rank"
        st.dataframe(best_movies, use_container_width=True, height=500)

    with col_t:
        st.markdown("#### 📺 Top 25 TV Shows")
        best_tvshows = (
            filtered_ranked[filtered_ranked["type"] == "TV Show"]
            .sort_values(["rating_tier", "release_year"], ascending=[True, False])
            .head(25)
            [best_cols]
            .reset_index(drop=True)
        )
        best_tvshows.index = best_tvshows.index + 1
        best_tvshows.index.name = "Rank"
        st.dataframe(best_tvshows, use_container_width=True, height=500)

    st.markdown("---")
    tier_labels = {
        1: "Tier 1 (R/TV-MA)", 2: "Tier 2 (PG-13/TV-14)", 3: "Tier 3 (PG/TV-PG)",
        4: "Tier 4 (G/TV-G)", 5: "Tier 5 (Kids TV)", 6: "Tier 6 (NR/UR)",
    }
    tier_dist = filtered_ranked["rating_tier"].map(tier_labels).value_counts().sort_index()
    tier_df = pd.DataFrame({"Tier": tier_dist.index, "Count": tier_dist.values})
    fig_tier = px.bar(
        tier_df, x="Tier", y="Count",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=[NETFLIX_RED],
        title="Content Distribution by Rating Tier",
    )
    fig_tier.update_layout(xaxis_title="", yaxis_title="Number of Titles", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_tier, use_container_width=True)

    st.markdown("##### 💡 Insight")
    top_tier = tier_df.iloc[0]
    st.info(
        f"**{top_tier['Tier']}** has the most content with **{top_tier['Count']:,}** titles. "
        f"This rating tier distribution reveals Netflix's target audience strategy — "
        f"the platform leans heavily into mature content aimed at adult viewers."
    )

# --- Tab 6: Top 10 by Country ---------------------------------------------------
with tab6:
    st.markdown("### 🌐 Top 10 Movies & TV Shows by Country")
    st.caption("Select a country to see the top 10 most recent movies and TV shows from that region.")

    all_countries = (
        filtered["primary_country"]
        .value_counts()
        .reset_index()
    )
    all_countries.columns = ["country", "count"]
    eligible_countries = all_countries[all_countries["count"] >= 5]["country"].tolist()

    selected_country = st.selectbox(
        "🌍 Select a Country",
        options=eligible_countries,
        index=0,
    )

    country_data = filtered[filtered["primary_country"] == selected_country]
    top_cols = ["title", "primary_genre", "release_year", "rating", "duration"]

    col_cm, col_ct = st.columns(2)

    with col_cm:
        st.markdown(f"#### 🎬 Top 10 Movies — {selected_country}")
        country_movies = (
            country_data[country_data["type"] == "Movie"]
            .sort_values("release_year", ascending=False)
            .head(10)
            [top_cols]
            .reset_index(drop=True)
        )
        if country_movies.empty:
            st.info(f"No movies found for {selected_country} with current filters.")
        else:
            country_movies.index = country_movies.index + 1
            country_movies.index.name = "Rank"
            st.dataframe(country_movies, use_container_width=True, height=420)

    with col_ct:
        st.markdown(f"#### 📺 Top 10 TV Shows — {selected_country}")
        country_tvshows = (
            country_data[country_data["type"] == "TV Show"]
            .sort_values("release_year", ascending=False)
            .head(10)
            [top_cols]
            .reset_index(drop=True)
        )
        if country_tvshows.empty:
            st.info(f"No TV shows found for {selected_country} with current filters.")
        else:
            country_tvshows.index = country_tvshows.index + 1
            country_tvshows.index.name = "Rank"
            st.dataframe(country_tvshows, use_container_width=True, height=420)

    st.markdown("---")
    total_country = len(country_data)
    movies_count = (country_data["type"] == "Movie").sum()
    tvshows_count = (country_data["type"] == "TV Show").sum()
    top_genre_country = country_data["primary_genre"].value_counts().idxmax() if not country_data.empty else "N/A"

    stat_cols = st.columns(4)
    stat_data = [
        ("Total Titles", f"{total_country:,}"),
        ("Movies", f"{movies_count:,}"),
        ("TV Shows", f"{tvshows_count:,}"),
        ("Top Genre", top_genre_country),
    ]
    for col, (label, value) in zip(stat_cols, stat_data):
        with col:
            st.markdown(
                f"""<div class="kpi-card">
                        <div class="kpi-value">{value}</div>
                        <div class="kpi-label">{label}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("")
    st.markdown("##### 💡 Insight")
    st.info(
        f"**{selected_country}** has **{total_country:,}** titles on Netflix in this filtered view, "
        f"with **{movies_count:,}** movies and **{tvshows_count:,}** TV shows. "
        f"The most popular genre from this country is **{top_genre_country}**."
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Built by Sasikumar Pulluri · pandas for data cleaning & feature engineering · "
    "Plotly for interactive visualization · Streamlit for the app layer · "
    "Dataset: Netflix Movies and TV Shows (Kaggle)"
)
