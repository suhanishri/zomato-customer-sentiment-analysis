from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
INPUT_SCORED = PROJECT_DIR / "analysis_zomato_full" / "results" / "full_dataset_scored_predictions.csv"
OUTPUT_DIR = BASE_DIR / "data"


THEME_ORDER = [
    "delivery",
    "refund_cancellation",
    "customer_support",
    "pricing_fees",
    "trust_reviews",
    "app_experience",
    "food_quality",
    "order_issue",
    "competitor_comparison",
    "other",
]


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_SCORED, low_memory=False)
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df["platform"] = df["platform"].fillna("unknown").astype(str).str.strip()
    df["theme_final"] = df["theme_final"].fillna("other").astype(str).str.strip()
    df["predicted_sentiment"] = df["predicted_sentiment"].fillna("neutral").astype(str).str.strip()
    df["recent_bucket"] = df["recent_bucket"].fillna("unknown").astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
    return df


def sentiment_counts(df: pd.DataFrame, group_cols: list[str], prefix: str = "") -> pd.DataFrame:
    out = (
        df.groupby(group_cols + ["predicted_sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ["negative", "neutral", "positive"]:
        if col not in out.columns:
            out[col] = 0
    out["total_rows"] = out[["negative", "neutral", "positive"]].sum(axis=1)
    out["negative_share"] = (out["negative"] / out["total_rows"]).round(4)
    out["neutral_share"] = (out["neutral"] / out["total_rows"]).round(4)
    out["positive_share"] = (out["positive"] / out["total_rows"]).round(4)
    out["net_sentiment"] = ((out["positive"] - out["negative"]) / out["total_rows"]).round(4)
    out["priority_score"] = (out["negative_share"] * out["total_rows"]).round(2)

    if prefix:
        rename_map = {
            "negative": f"negative_{prefix}",
            "neutral": f"neutral_{prefix}",
            "positive": f"positive_{prefix}",
            "total_rows": f"total_rows_{prefix}",
            "negative_share": f"negative_share_{prefix}",
            "neutral_share": f"neutral_share_{prefix}",
            "positive_share": f"positive_share_{prefix}",
            "net_sentiment": f"net_sentiment_{prefix}",
            "priority_score": f"priority_score_{prefix}",
        }
        out = out.rename(columns=rename_map)
    return out


def build_overview_kpis(df: pd.DataFrame) -> dict:
    overall = df["predicted_sentiment"].value_counts()
    recent = df[df["recent_bucket"] == "2024_plus"].copy()
    theme_summary = sentiment_counts(df, ["theme_final"])
    theme_summary["theme_order"] = theme_summary["theme_final"].map({k: i for i, k in enumerate(THEME_ORDER)}).fillna(999)
    theme_summary = theme_summary.sort_values(["theme_order", "total_rows"]).drop(columns=["theme_order"])

    top_priority = theme_summary.sort_values(["priority_score", "negative_share"], ascending=[False, False]).head(5)
    top_positive = theme_summary.sort_values(["positive_share", "total_rows"], ascending=[False, False]).head(5)
    top_negative = theme_summary.sort_values(["negative_share", "total_rows"], ascending=[False, False]).head(5)

    return {
        "total_rows": int(len(df)),
        "play_store_rows": int((df["platform"] == "google_play").sum()),
        "positive_rows": int(overall.get("positive", 0)),
        "negative_rows": int(overall.get("negative", 0)),
        "neutral_rows": int(overall.get("neutral", 0)),
        "positive_share": round(float(overall.get("positive", 0) / len(df)), 4),
        "negative_share": round(float(overall.get("negative", 0) / len(df)), 4),
        "neutral_share": round(float(overall.get("neutral", 0) / len(df)), 4),
        "recent_2024_plus_rows": int(len(recent)),
        "recent_2024_plus_share": round(float(len(recent) / len(df)), 4),
        "top_priority_themes": top_priority.to_dict(orient="records"),
        "top_negative_themes": top_negative.to_dict(orient="records"),
        "top_positive_themes": top_positive.to_dict(orient="records"),
    }


def top_examples(df: pd.DataFrame, sentiment: str, per_theme: int = 5) -> pd.DataFrame:
    prob_col = f"predicted_{sentiment}_prob"
    subset = df[df["predicted_sentiment"] == sentiment].copy()
    subset = subset.sort_values(["theme_final", prob_col, "likes"], ascending=[True, False, False])
    cols = ["theme_final", "platform", "created_at", "likes", prob_col, "text"]
    return subset.groupby("theme_final", group_keys=False).head(per_theme)[cols]


def main() -> None:
    ensure_dirs()
    df = load_data()
    generated_files = [
        "overview_kpis.json",
        "sentiment_by_theme.csv",
        "sentiment_by_theme_2024_plus.csv",
        "sentiment_by_year.csv",
        "theme_priority.csv",
        "top_negative_examples_by_theme.csv",
        "top_positive_examples_by_theme.csv",
        "dashboard_metadata.json",
    ]

    overview = build_overview_kpis(df)
    save_json(OUTPUT_DIR / "overview_kpis.json", overview)

    theme_summary = sentiment_counts(df, ["theme_final"])
    theme_summary["theme_order"] = theme_summary["theme_final"].map({k: i for i, k in enumerate(THEME_ORDER)}).fillna(999)
    theme_summary = theme_summary.sort_values(["theme_order", "total_rows"], ascending=[True, False]).drop(columns=["theme_order"])
    theme_summary.to_csv(OUTPUT_DIR / "sentiment_by_theme.csv", index=False)

    year_df = df[df["year"].notna()].copy()
    year_df["year"] = year_df["year"].astype(int)
    sentiment_counts(year_df, ["year"]).to_csv(OUTPUT_DIR / "sentiment_by_year.csv", index=False)

    recent_df = df[df["recent_bucket"] == "2024_plus"].copy()
    if not recent_df.empty:
        recent_theme = sentiment_counts(recent_df, ["theme_final"], prefix="2024_plus")
        recent_theme["theme_order"] = recent_theme["theme_final"].map({k: i for i, k in enumerate(THEME_ORDER)}).fillna(999)
        recent_theme = recent_theme.sort_values(["theme_order", "total_rows_2024_plus"], ascending=[True, False]).drop(columns=["theme_order"])
        recent_theme.to_csv(OUTPUT_DIR / "sentiment_by_theme_2024_plus.csv", index=False)

    priority = theme_summary.sort_values(["priority_score", "negative_share"], ascending=[False, False])
    priority.to_csv(OUTPUT_DIR / "theme_priority.csv", index=False)

    top_examples(df, "negative").to_csv(OUTPUT_DIR / "top_negative_examples_by_theme.csv", index=False)
    top_examples(df, "positive").to_csv(OUTPUT_DIR / "top_positive_examples_by_theme.csv", index=False)

    metadata = {
        "input_file": str(INPUT_SCORED),
        "rows": int(len(df)),
        "generated_files": generated_files,
    }
    save_json(OUTPUT_DIR / "dashboard_metadata.json", metadata)

    print(json.dumps({
        "rows": int(len(df)),
        "output_dir": str(OUTPUT_DIR),
        "generated_files": metadata["generated_files"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
