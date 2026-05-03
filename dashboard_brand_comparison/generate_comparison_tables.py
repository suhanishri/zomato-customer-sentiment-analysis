from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
ZOMATO_INPUT = PROJECT_DIR / "master_final_dataset" / "master_final_dataset.csv"
SWIGGY_INPUT = PROJECT_DIR / "master_final_dataset_swiggy" / "master_final_dataset.csv"
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


def load_brand(path: Path, brand_name: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df = df[df["platform"] == "google_play"].copy()
    df["brand"] = brand_name
    df["theme_final"] = df["theme_final"].fillna("other").astype(str).str.strip()
    df["sentiment_label"] = df["sentiment_label"].fillna("neutral").astype(str).str.strip()
    df["recent_bucket"] = df["recent_bucket"].fillna("unknown").astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def sentiment_counts(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    out = (
        df.groupby(group_cols + ["sentiment_label"])
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
    return out


def main() -> None:
    ensure_dirs()
    zomato = load_brand(ZOMATO_INPUT, "zomato")
    swiggy = load_brand(SWIGGY_INPUT, "swiggy")
    combined = pd.concat([zomato, swiggy], ignore_index=True)

    overview = sentiment_counts(combined, ["brand"])
    overview.to_csv(OUTPUT_DIR / "comparison_overview.csv", index=False)

    by_theme = sentiment_counts(combined, ["brand", "theme_final"])
    by_theme["theme_order"] = by_theme["theme_final"].map({k: i for i, k in enumerate(THEME_ORDER)}).fillna(999)
    by_theme = by_theme.sort_values(["theme_order", "brand"]).drop(columns=["theme_order"])
    by_theme.to_csv(OUTPUT_DIR / "comparison_by_theme.csv", index=False)

    recent = combined[combined["recent_bucket"] == "2024_plus"].copy()
    recent_by_theme = sentiment_counts(recent, ["brand", "theme_final"])
    recent_by_theme["theme_order"] = recent_by_theme["theme_final"].map({k: i for i, k in enumerate(THEME_ORDER)}).fillna(999)
    recent_by_theme = recent_by_theme.sort_values(["theme_order", "brand"]).drop(columns=["theme_order"])
    recent_by_theme.to_csv(OUTPUT_DIR / "comparison_by_theme_2024_plus.csv", index=False)

    by_year = combined[combined["year"].notna()].copy()
    by_year["year"] = by_year["year"].astype(int)
    sentiment_counts(by_year, ["brand", "year"]).to_csv(OUTPUT_DIR / "comparison_by_year.csv", index=False)

    pivot_neg = by_theme.pivot(index="theme_final", columns="brand", values="negative_share").reset_index()
    pivot_net = by_theme.pivot(index="theme_final", columns="brand", values="net_sentiment").reset_index()
    theme_gap = by_theme.pivot(index="theme_final", columns="brand", values=["negative_share", "positive_share", "net_sentiment", "total_rows"])
    theme_gap.columns = [f"{a}_{b}" for a, b in theme_gap.columns]
    theme_gap = theme_gap.reset_index()
    theme_gap["negative_share_gap_zomato_minus_swiggy"] = (theme_gap["negative_share_zomato"] - theme_gap["negative_share_swiggy"]).round(4)
    theme_gap["net_sentiment_gap_zomato_minus_swiggy"] = (theme_gap["net_sentiment_zomato"] - theme_gap["net_sentiment_swiggy"]).round(4)
    theme_gap = theme_gap.sort_values("negative_share_gap_zomato_minus_swiggy", ascending=False)
    theme_gap.to_csv(OUTPUT_DIR / "comparison_theme_gap.csv", index=False)

    summary = {
        "rows_google_only_zomato": int(len(zomato)),
        "rows_google_only_swiggy": int(len(swiggy)),
        "zomato_sentiment_counts": zomato["sentiment_label"].value_counts().to_dict(),
        "swiggy_sentiment_counts": swiggy["sentiment_label"].value_counts().to_dict(),
        "top_theme_gaps_negative_share": theme_gap.head(5).to_dict(orient="records"),
        "comparison_note": "Comparison tables use Google Play only and final weak sentiment labels for both brands.",
    }
    save_json(OUTPUT_DIR / "comparison_summary.json", summary)

    print(json.dumps({
        "rows_combined": int(len(combined)),
        "output_dir": str(OUTPUT_DIR),
        "generated_files": sorted(p.name for p in OUTPUT_DIR.iterdir()),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
