from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
INPUT_CSV = PROJECT_DIR / "master_final_dataset" / "master_final_dataset.csv"
RESULTS_DIR = BASE_DIR / "results"
BEST_MODEL_PATH = RESULTS_DIR / "best_sentiment_pipeline.joblib"
LEGACY_MODEL_PATH = RESULTS_DIR / "baseline_logreg_pipeline.joblib"


THEME_DISPLAY_ORDER = [
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


def save_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df["theme_final"] = df["theme_final"].fillna("other").astype(str).str.strip()
    df["platform"] = df["platform"].fillna("").astype(str).str.strip()
    df["recent_bucket"] = df["recent_bucket"].fillna("unknown").astype(str).str.strip()
    df["created_at"] = df["created_at"].fillna("").astype(str).str.strip()
    return df


def theme_summary(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df.groupby(["theme_final", "predicted_sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for col in ["negative", "neutral", "positive"]:
        if col not in counts.columns:
            counts[col] = 0

    counts["total_rows"] = counts[["negative", "neutral", "positive"]].sum(axis=1)
    counts["negative_share"] = (counts["negative"] / counts["total_rows"]).round(4)
    counts["neutral_share"] = (counts["neutral"] / counts["total_rows"]).round(4)
    counts["positive_share"] = (counts["positive"] / counts["total_rows"]).round(4)
    counts["net_sentiment"] = ((counts["positive"] - counts["negative"]) / counts["total_rows"]).round(4)
    counts["priority_score"] = (counts["negative_share"] * counts["total_rows"]).round(2)

    order_map = {name: idx for idx, name in enumerate(THEME_DISPLAY_ORDER)}
    counts["theme_order"] = counts["theme_final"].map(order_map).fillna(999)
    counts = counts.sort_values(["theme_order", "total_rows"], ascending=[True, False]).drop(columns=["theme_order"])
    return counts


def theme_recent_summary(df: pd.DataFrame) -> pd.DataFrame:
    recent = df[df["recent_bucket"] == "2024_plus"].copy()
    if recent.empty:
        return pd.DataFrame()
    out = theme_summary(recent)
    out = out.rename(
        columns={
            "negative": "negative_2024_plus",
            "neutral": "neutral_2024_plus",
            "positive": "positive_2024_plus",
            "total_rows": "total_rows_2024_plus",
            "negative_share": "negative_share_2024_plus",
            "neutral_share": "neutral_share_2024_plus",
            "positive_share": "positive_share_2024_plus",
            "net_sentiment": "net_sentiment_2024_plus",
            "priority_score": "priority_score_2024_plus",
        }
    )
    return out


def theme_platform_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby(["platform", "theme_final", "predicted_sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ["negative", "neutral", "positive"]:
        if col not in out.columns:
            out[col] = 0
    out["total_rows"] = out[["negative", "neutral", "positive"]].sum(axis=1)
    out["negative_share"] = (out["negative"] / out["total_rows"]).round(4)
    out["positive_share"] = (out["positive"] / out["total_rows"]).round(4)
    out["net_sentiment"] = ((out["positive"] - out["negative"]) / out["total_rows"]).round(4)
    return out.sort_values(["platform", "total_rows"], ascending=[True, False])


def top_negative_examples(df: pd.DataFrame, per_theme: int = 5) -> pd.DataFrame:
    negatives = df[df["predicted_sentiment"] == "negative"].copy()
    negatives = negatives.sort_values(
        ["theme_final", "predicted_negative_prob", "likes"],
        ascending=[True, False, False],
    )
    cols = [
        "theme_final",
        "platform",
        "created_at",
        "likes",
        "predicted_negative_prob",
        "text",
    ]
    return negatives.groupby("theme_final", group_keys=False).head(per_theme)[cols]


def top_positive_examples(df: pd.DataFrame, per_theme: int = 5) -> pd.DataFrame:
    positives = df[df["predicted_sentiment"] == "positive"].copy()
    positives = positives.sort_values(
        ["theme_final", "predicted_positive_prob", "likes"],
        ascending=[True, False, False],
    )
    cols = [
        "theme_final",
        "platform",
        "created_at",
        "likes",
        "predicted_positive_prob",
        "text",
    ]
    return positives.groupby("theme_final", group_keys=False).head(per_theme)[cols]


def main() -> None:
    model_path = BEST_MODEL_PATH if BEST_MODEL_PATH.exists() else LEGACY_MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(
            f"Missing trained model. Checked: {BEST_MODEL_PATH} and {LEGACY_MODEL_PATH}"
        )

    df = load_data()
    model = joblib.load(model_path)

    probs = model.predict_proba(df["text"])
    prob_df = pd.DataFrame(probs, columns=[f"predicted_{c}_prob" for c in model.named_steps["clf"].classes_], index=df.index)
    pred_labels = model.predict(df["text"])

    scored = pd.concat([df, prob_df], axis=1)
    scored["predicted_sentiment"] = pred_labels
    scored["likes"] = pd.to_numeric(scored["likes"], errors="coerce").fillna(0).astype(int)

    scored.to_csv(RESULTS_DIR / "full_dataset_scored_predictions.csv", index=False)

    overall_theme = theme_summary(scored)
    overall_theme.to_csv(RESULTS_DIR / "theme_sentiment_summary.csv", index=False)

    recent_theme = theme_recent_summary(scored)
    if not recent_theme.empty:
        recent_theme.to_csv(RESULTS_DIR / "theme_sentiment_summary_2024_plus.csv", index=False)

    platform_theme = theme_platform_summary(scored)
    platform_theme.to_csv(RESULTS_DIR / "theme_sentiment_by_platform.csv", index=False)

    negative_examples = top_negative_examples(scored)
    negative_examples.to_csv(RESULTS_DIR / "top_negative_examples_by_theme.csv", index=False)

    positive_examples = top_positive_examples(scored)
    positive_examples.to_csv(RESULTS_DIR / "top_positive_examples_by_theme.csv", index=False)

    top_negative_themes = overall_theme.sort_values(["negative_share", "total_rows"], ascending=[False, False]).head(5)
    top_priority_themes = overall_theme.sort_values(["priority_score", "negative_share"], ascending=[False, False]).head(5)
    top_positive_themes = overall_theme.sort_values(["positive_share", "total_rows"], ascending=[False, False]).head(5)

    summary = {
        "rows_scored": int(len(scored)),
        "model_path": str(model_path),
        "predicted_sentiment_counts": scored["predicted_sentiment"].value_counts().to_dict(),
        "top_negative_themes_by_share": top_negative_themes.to_dict(orient="records"),
        "top_priority_themes_by_volume_x_negative_share": top_priority_themes.to_dict(orient="records"),
        "top_positive_themes_by_share": top_positive_themes.to_dict(orient="records"),
    }
    save_json(RESULTS_DIR / "theme_analysis_summary.json", summary)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
