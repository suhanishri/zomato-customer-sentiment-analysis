from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DATA_DIR = PROJECT_DIR / "dashboard_zomato" / "data"
COMPARISON_DATA_DIR = PROJECT_DIR / "dashboard_brand_comparison" / "data"
ANALYSIS_RESULTS_DIR = PROJECT_DIR / "analysis_zomato_full" / "results"


@st.cache_data
def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_data():
    overview = load_json(DATA_DIR / "overview_kpis.json")
    sentiment_by_theme = load_csv(DATA_DIR / "sentiment_by_theme.csv")
    sentiment_by_theme_recent = load_csv(DATA_DIR / "sentiment_by_theme_2024_plus.csv")
    sentiment_by_year = load_csv(DATA_DIR / "sentiment_by_year.csv")
    theme_priority = load_csv(DATA_DIR / "theme_priority.csv")
    top_negative_examples = load_csv(DATA_DIR / "top_negative_examples_by_theme.csv")
    top_positive_examples = load_csv(DATA_DIR / "top_positive_examples_by_theme.csv")
    return {
        "overview": overview,
        "sentiment_by_theme": sentiment_by_theme,
        "sentiment_by_theme_recent": sentiment_by_theme_recent,
        "sentiment_by_year": sentiment_by_year,
        "theme_priority": theme_priority,
        "top_negative_examples": top_negative_examples,
        "top_positive_examples": top_positive_examples,
    }


def load_comparison_data():
    if not COMPARISON_DATA_DIR.exists():
        return None
    required = [
        COMPARISON_DATA_DIR / "comparison_summary.json",
        COMPARISON_DATA_DIR / "comparison_overview.csv",
        COMPARISON_DATA_DIR / "comparison_by_theme.csv",
        COMPARISON_DATA_DIR / "comparison_by_theme_2024_plus.csv",
        COMPARISON_DATA_DIR / "comparison_by_year.csv",
        COMPARISON_DATA_DIR / "comparison_theme_gap.csv",
    ]
    if not all(p.exists() for p in required):
        return None
    return {
        "summary": load_json(COMPARISON_DATA_DIR / "comparison_summary.json"),
        "overview": load_csv(COMPARISON_DATA_DIR / "comparison_overview.csv"),
        "by_theme": load_csv(COMPARISON_DATA_DIR / "comparison_by_theme.csv"),
        "by_theme_recent": load_csv(COMPARISON_DATA_DIR / "comparison_by_theme_2024_plus.csv"),
        "by_year": load_csv(COMPARISON_DATA_DIR / "comparison_by_year.csv"),
        "theme_gap": load_csv(COMPARISON_DATA_DIR / "comparison_theme_gap.csv"),
    }


def load_benchmark_data():
    required = [
        ANALYSIS_RESULTS_DIR / "model_benchmark.csv",
        ANALYSIS_RESULTS_DIR / "model_benchmark_literature.csv",
        ANALYSIS_RESULTS_DIR / "model_benchmark_literature.json",
        ANALYSIS_RESULTS_DIR / "benchmark_examples_best_vs_random_forest.csv",
    ]
    if not all(path.exists() for path in required):
        return None
    return {
        "benchmark": load_csv(ANALYSIS_RESULTS_DIR / "model_benchmark.csv"),
        "literature": load_csv(ANALYSIS_RESULTS_DIR / "model_benchmark_literature.csv"),
        "summary": load_json(ANALYSIS_RESULTS_DIR / "model_benchmark_literature.json"),
        "best_vs_rf_examples": load_csv(ANALYSIS_RESULTS_DIR / "benchmark_examples_best_vs_random_forest.csv"),
    }


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_sentiment_bar(df: pd.DataFrame, x: str, title: str):
    melted = df.melt(
        id_vars=[x],
        value_vars=["negative_share", "neutral_share", "positive_share"],
        var_name="sentiment",
        value_name="share",
    )
    label_map = {
        "negative_share": "Negative",
        "neutral_share": "Neutral",
        "positive_share": "Positive",
    }
    melted["sentiment"] = melted["sentiment"].map(label_map)
    fig = px.bar(
        melted,
        x=x,
        y="share",
        color="sentiment",
        barmode="group",
        title=title,
        color_discrete_map={
            "Negative": "#b22222",
            "Neutral": "#d4a017",
            "Positive": "#1f7a1f",
        },
    )
    fig.update_layout(yaxis_tickformat=".0%")
    return fig


def build_net_sentiment_chart(df: pd.DataFrame, x: str, title: str):
    chart_df = df.copy()
    chart_df["net_sentiment_label"] = chart_df["net_sentiment"].map(lambda value: f"{value:.1%}")
    fig = px.bar(
        chart_df,
        x=x,
        y="net_sentiment",
        title=title,
        color="net_sentiment",
        text="net_sentiment_label",
        color_continuous_scale=["#b22222", "#f4d35e", "#1f7a1f"],
        color_continuous_midpoint=0,
        range_color=[-1, 1],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_tickformat=".0%", coloraxis_colorbar_title="Net sentiment")
    return fig


def build_brand_compare_bar(df: pd.DataFrame, x: str, metric: str, title: str):
    fig = px.bar(
        df,
        x=x,
        y=metric,
        color="brand",
        barmode="group",
        title=title,
        color_discrete_map={
            "zomato": "#d62828",
            "swiggy": "#f77f00",
        },
    )
    if "share" in metric or "sentiment" in metric:
        fig.update_layout(yaxis_tickformat=".0%")
    return fig


def build_overall_share_chart(overview: dict):
    df = pd.DataFrame(
        {
            "sentiment": ["Negative", "Neutral", "Positive"],
            "share": [
                overview["negative_share"],
                overview["neutral_share"],
                overview["positive_share"],
            ],
        }
    )
    fig = px.bar(
        df,
        x="sentiment",
        y="share",
        title="Overall Sentiment Share",
        color="sentiment",
        color_discrete_map={
            "Negative": "#b22222",
            "Neutral": "#d4a017",
            "Positive": "#1f7a1f",
        },
    )
    fig.update_layout(yaxis_tickformat=".0%")
    return fig


def build_metric_compare_chart(df: pd.DataFrame, metric: str, title: str):
    chart_df = df[["model_label", metric]].copy()
    chart_df = chart_df.rename(columns={metric: "score"})
    fig = px.bar(
        chart_df,
        x="model_label",
        y="score",
        title=title,
        color="model_label",
        color_discrete_sequence=["#d62828", "#1d3557", "#f77f00"],
    )
    fig.update_layout(showlegend=False, yaxis_tickformat=".0%")
    return fig


def build_class_metric_chart(df: pd.DataFrame, metric_prefix: str, title: str):
    cols = [
        "negative_" + metric_prefix,
        "neutral_" + metric_prefix,
        "positive_" + metric_prefix,
    ]
    chart_df = df[["model_label"] + cols].copy()
    melted = chart_df.melt(id_vars=["model_label"], value_vars=cols, var_name="metric", value_name="score")
    label_map = {
        f"negative_{metric_prefix}": "Negative",
        f"neutral_{metric_prefix}": "Neutral",
        f"positive_{metric_prefix}": "Positive",
    }
    melted["class"] = melted["metric"].map(label_map)
    fig = px.bar(
        melted,
        x="class",
        y="score",
        color="model_label",
        barmode="group",
        title=title,
        color_discrete_sequence=["#d62828", "#1d3557", "#f77f00"],
    )
    fig.update_layout(yaxis_tickformat=".0%")
    return fig


def build_superiority_table(display_df: pd.DataFrame) -> pd.DataFrame:
    best = display_df[display_df["model_label"] == "SentiLens"]
    paper = display_df[display_df["model_label"] == "Random Forest (paper-reported)"]
    recreated_rf = display_df[display_df["model_label"] == "TF-IDF + Random Forest"]

    if best.empty:
        return pd.DataFrame()

    best_row = best.iloc[0]
    comparisons: list[dict[str, object]] = []

    metric_specs = [
        ("accuracy", "Accuracy"),
        ("average_precision", "Average Precision"),
        ("average_recall", "Average Recall"),
        ("negative_precision", "Negative Precision"),
        ("negative_recall", "Negative Recall"),
        ("neutral_precision", "Neutral Precision"),
        ("neutral_recall", "Neutral Recall"),
        ("positive_precision", "Positive Precision"),
        ("positive_recall", "Positive Recall"),
    ]

    if not paper.empty:
        paper_row = paper.iloc[0]
        for metric_key, metric_label in metric_specs:
            best_value = best_row.get(metric_key)
            paper_value = paper_row.get(metric_key)
            if pd.notna(best_value) and pd.notna(paper_value) and float(best_value) > float(paper_value):
                comparisons.append(
                    {
                        "comparison_to": "Paper-reported Random Forest",
                        "metric": metric_label,
                        "our_best_model": round(float(best_value), 4),
                        "other_model": round(float(paper_value), 4),
                        "absolute_gap": round(float(best_value) - float(paper_value), 4),
                    }
                )

    if not recreated_rf.empty:
        rf_row = recreated_rf.iloc[0]
        for metric_key, metric_label in metric_specs:
            best_value = best_row.get(metric_key)
            rf_value = rf_row.get(metric_key)
            if pd.notna(best_value) and pd.notna(rf_value) and float(best_value) > float(rf_value):
                comparisons.append(
                    {
                        "comparison_to": "Our recreated Random Forest",
                        "metric": metric_label,
                        "our_best_model": round(float(best_value), 4),
                        "other_model": round(float(rf_value), 4),
                        "absolute_gap": round(float(best_value) - float(rf_value), 4),
                    }
                )

    return pd.DataFrame(comparisons)


def main():
    st.set_page_config(
        page_title="Zomato Sentiment Dashboard",
        page_icon="🍽️",
        layout="wide",
    )

    data = load_data()
    comparison = load_comparison_data()
    benchmark = load_benchmark_data()
    overview = data["overview"]

    st.title("Zomato Sentiment Dashboard")
    st.caption("Google Play Store review analytics dashboard for the Zomato sentiment project.")

    with st.sidebar:
        st.header("About")
        st.write("This dashboard summarizes sentiment patterns for Zomato using the Google Play-only final dataset.")
        theme_choice = st.selectbox(
            "Select Theme",
            ["All"] + data["sentiment_by_theme"]["theme_final"].tolist(),
            index=0,
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows", f"{overview['total_rows']:,}")
    c2.metric("Positive Share", format_pct(overview["positive_share"]))
    c3.metric("Negative Share", format_pct(overview["negative_share"]))
    c4.metric("Recent Rows (2024+)", f"{overview['recent_2024_plus_rows']:,}")

    c5, c6, c7 = st.columns(3)
    c5.metric("Play Store Rows", f"{overview['play_store_rows']:,}")
    c6.metric("Neutral Share", format_pct(overview["neutral_share"]))
    c7.metric("Themes Tracked", f"{len(data['sentiment_by_theme']):,}")

    tab_main, tab_benchmark, tab_compare = st.tabs(["Zomato Analysis", "Benchmark vs Paper", "Zomato vs Swiggy"])

    with tab_main:
        st.subheader("Overall Sentiment")
        st.plotly_chart(
            build_overall_share_chart(overview),
            use_container_width=True,
        )

        st.subheader("Theme Analysis")
        theme_df = data["sentiment_by_theme"].copy()
        recent_theme_df = data["sentiment_by_theme_recent"].copy()
        priority_df = data["theme_priority"].copy()

        if theme_choice != "All":
            theme_df = theme_df[theme_df["theme_final"] == theme_choice]
            recent_theme_df = recent_theme_df[recent_theme_df["theme_final"] == theme_choice]
            priority_df = priority_df[priority_df["theme_final"] == theme_choice]

        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                build_sentiment_bar(theme_df, "theme_final", "Sentiment Share by Theme"),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(
                build_net_sentiment_chart(theme_df, "theme_final", "Net Sentiment by Theme"),
                use_container_width=True,
            )

        st.subheader("Priority Themes")
        st.dataframe(
            priority_df[[
                "theme_final",
                "total_rows",
                "negative",
                "positive",
                "negative_share",
                "positive_share",
                "net_sentiment",
                "priority_score",
            ]],
            use_container_width=True,
        )

        st.subheader("Recent Theme View (2024+)")
        if not recent_theme_df.empty:
            st.dataframe(recent_theme_df, use_container_width=True)
        else:
            st.info("No recent data available for the selected view.")

        st.subheader("Trend Over Time")
        year_df = data["sentiment_by_year"].copy().sort_values("year")
        st.plotly_chart(
            build_sentiment_bar(year_df, "year", "Sentiment Share by Year"),
            use_container_width=True,
        )

        st.subheader("Example Comments")
        example_source = st.radio(
            "Example Comments Shown",
            ["Negative examples", "Positive examples"],
            index=0,
            help="This changes the Example Comments table shown below.",
            horizontal=True,
        )
        st.caption(f"Showing: {example_source}")
        examples = data["top_negative_examples"] if example_source == "Negative examples" else data["top_positive_examples"]
        if theme_choice != "All":
            examples = examples[examples["theme_final"] == theme_choice]
        st.dataframe(examples, use_container_width=True)

    with tab_benchmark:
        st.subheader("Literature Benchmark")
        st.caption(
            "This view compares the paper-reported Random Forest metrics with our recreated Random Forest benchmark "
            "and our best-performing model on the Google Play-only Zomato dataset."
        )

        if benchmark is None:
            st.warning("Benchmark files have not been generated yet.")
        else:
            literature_df = benchmark["literature"].copy()
            summary = benchmark["summary"]
            display_df = literature_df[
                literature_df["model_label"].isin(
                    [
                        "Random Forest (paper-reported)",
                        "TF-IDF + Random Forest",
                        "SentiLens",
                    ]
                )
            ].copy()

            if not display_df.empty:
                b1, b2, b3 = st.columns(3)
                paper_acc = display_df.loc[display_df["model_label"] == "Random Forest (paper-reported)", "accuracy"]
                rf_acc = display_df.loc[display_df["model_label"] == "TF-IDF + Random Forest", "accuracy"]
                best_acc = display_df.loc[display_df["model_label"] == "SentiLens", "accuracy"]
                b1.metric("Paper Accuracy", format_pct(float(paper_acc.iloc[0])) if not paper_acc.empty else "NA")
                b2.metric("Our RF Accuracy", format_pct(float(rf_acc.iloc[0])) if not rf_acc.empty else "NA")
                b3.metric("SentiLens Accuracy", format_pct(float(best_acc.iloc[0])) if not best_acc.empty else "NA")

                left, right = st.columns(2)
                with left:
                    st.plotly_chart(
                        build_metric_compare_chart(
                            display_df,
                            "accuracy",
                            "Accuracy Comparison",
                        ),
                        use_container_width=True,
                    )
                with right:
                    st.plotly_chart(
                        build_metric_compare_chart(
                            display_df,
                            "average_recall",
                            "Average Recall Comparison",
                        ),
                        use_container_width=True,
                    )

                left, right = st.columns(2)
                with left:
                    st.plotly_chart(
                        build_class_metric_chart(
                            display_df,
                            "precision",
                            "Class-wise Precision",
                        ),
                        use_container_width=True,
                    )
                with right:
                    st.plotly_chart(
                        build_class_metric_chart(
                            display_df,
                            "recall",
                            "Class-wise Recall",
                        ),
                        use_container_width=True,
                    )

                st.subheader("Benchmark Table")
                metric_cols = [
                    "model_label",
                    "accuracy",
                    "average_precision",
                    "average_recall",
                    "negative_precision",
                    "negative_recall",
                    "neutral_precision",
                    "neutral_recall",
                    "positive_precision",
                    "positive_recall",
                    "dataset_note",
                ]
                st.dataframe(display_df[metric_cols], use_container_width=True)

                superiority_df = build_superiority_table(display_df)
                st.subheader("Performance Advantages of SentiLens")
                if superiority_df.empty:
                    st.info("No superiority metrics were found for the currently displayed comparison rows.")
                else:
                    st.dataframe(superiority_df, use_container_width=True)

                st.subheader("Examples Where SentiLens Beat Random Forest")
                example_df = benchmark["best_vs_rf_examples"].copy()
                if theme_choice != "All":
                    example_df = example_df[example_df["theme_final"] == theme_choice]
                example_df = example_df.head(12)
                example_df = example_df.rename(
                    columns={
                        "text": "customer_review",
                        "sentiment_label": "actual_sentiment",
                        "best_model_prediction": "sentilens_prediction",
                        "random_forest_prediction": "random_forest_prediction",
                        "best_model_confidence": "sentilens_confidence",
                        "random_forest_confidence": "random_forest_confidence",
                    }
                )
                example_cols = [
                    "theme_final",
                    "actual_sentiment",
                    "sentilens_prediction",
                    "random_forest_prediction",
                    "sentilens_confidence",
                    "random_forest_confidence",
                    "customer_review",
                ]
                if example_df.empty:
                    st.info("No holdout examples found for the selected theme where our best model beat Random Forest.")
                else:
                    st.dataframe(example_df[example_cols], use_container_width=True)

                st.subheader("Comparison Note")
                st.info(summary["comparison_note"])

    with tab_compare:
        st.subheader("Competitor Benchmark")
        st.caption("This comparison uses Google Play only for both brands and uses the final weak sentiment labels to keep the benchmark fair.")

        if comparison is None:
            st.warning("Comparison data has not been generated yet.")
        else:
            comp_summary = comparison["summary"]
            comp_overview = comparison["overview"].copy()
            comp_by_theme = comparison["by_theme"].copy()
            comp_by_theme_recent = comparison["by_theme_recent"].copy()
            comp_by_year = comparison["by_year"].copy().sort_values(["year", "brand"])
            comp_gap = comparison["theme_gap"].copy()

            cc1, cc2, cc3, cc4 = st.columns(4)
            cc1.metric("Zomato Rows", f"{comp_summary['rows_google_only_zomato']:,}")
            cc2.metric("Swiggy Rows", f"{comp_summary['rows_google_only_swiggy']:,}")
            cc3.metric("Zomato Negative", f"{comp_summary['zomato_sentiment_counts'].get('negative', 0):,}")
            cc4.metric("Swiggy Negative", f"{comp_summary['swiggy_sentiment_counts'].get('negative', 0):,}")

            left, right = st.columns(2)
            with left:
                st.plotly_chart(
                    build_brand_compare_bar(comp_overview, "brand", "negative_share", "Negative Share by Brand"),
                    use_container_width=True,
                )
            with right:
                st.plotly_chart(
                    build_brand_compare_bar(comp_overview, "brand", "positive_share", "Positive Share by Brand"),
                    use_container_width=True,
                )

            compare_theme_df = comp_by_theme.copy()
            if theme_choice != "All":
                compare_theme_df = compare_theme_df[compare_theme_df["theme_final"] == theme_choice]

            left, right = st.columns(2)
            with left:
                st.plotly_chart(
                    build_brand_compare_bar(compare_theme_df, "theme_final", "negative_share", "Negative Share by Theme and Brand"),
                    use_container_width=True,
                )
            with right:
                st.plotly_chart(
                    build_brand_compare_bar(compare_theme_df, "theme_final", "net_sentiment", "Net Sentiment by Theme and Brand"),
                    use_container_width=True,
                )

            st.subheader("Theme Gap Table")
            gap_df = comp_gap.copy()
            if theme_choice != "All":
                gap_df = gap_df[gap_df["theme_final"] == theme_choice]
            st.dataframe(gap_df, use_container_width=True)

            st.subheader("Recent Comparison (2024+)")
            recent_compare_df = comp_by_theme_recent.copy()
            if theme_choice != "All":
                recent_compare_df = recent_compare_df[recent_compare_df["theme_final"] == theme_choice]
            st.dataframe(recent_compare_df, use_container_width=True)

            st.subheader("Brand Trend Over Time")
            st.plotly_chart(
                build_brand_compare_bar(comp_by_year, "year", "negative_share", "Negative Share by Year and Brand"),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
