import json
import argparse
from pathlib import Path

import pandas as pd


DEFAULT_GOOGLE_INPUT = "merged_google_reviews/google_reviews_master_cleaned.csv"
DEFAULT_OUTPUT_DIR = "master_sentiment_dataset"


def normalize_text_series(s: pd.Series) -> pd.Series:
    return (
        s.fillna("")
         .astype(str)
         .str.lower()
         .str.replace(r"[^\w\s]", " ", regex=True)
         .str.replace(r"\s+", " ", regex=True)
         .str.strip()
    )


def safe_read_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing input file: {p}")
    df = pd.read_csv(p)
    if df.empty:
        print(f"[warn] Empty CSV: {p}")
    return df


def get_series(df: pd.DataFrame, col: str, default="") -> pd.Series:
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), index=df.index)


def standardize_google(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["platform"] = "google_play"
    out["source_type_master"] = get_series(out, "theme_hint", "other").fillna("other").astype(str)
    out["record_id"] = get_series(out, "source_id", "").fillna("").astype(str)
    out["parent_id"] = get_series(out, "parent_id", "").fillna("").astype(str)
    out["text"] = get_series(out, "text", "").fillna("").astype(str)
    out["title"] = get_series(out, "title", "").fillna("").astype(str)
    out["author"] = get_series(out, "author", "").fillna("").astype(str)
    out["created_at"] = get_series(out, "created_at", "").fillna("").astype(str)
    out["likes"] = pd.to_numeric(get_series(out, "thumbs_up_count", 0), errors="coerce").fillna(0).astype(int)
    out["reply_count"] = pd.to_numeric(get_series(out, "reply_count", 0), errors="coerce").fillna(0).astype(int)
    out["rating"] = pd.to_numeric(get_series(out, "score", None), errors="coerce")
    out["relevance_score"] = pd.to_numeric(get_series(out, "relevance_score", 0), errors="coerce")
    out["brand"] = "zomato"
    out["query_used"] = get_series(out, "search_query", "").fillna("").astype(str)
    out["source_file"] = get_series(out, "source_file", "").fillna("").astype(str)
    out["source_folder"] = get_series(out, "source_folder", "").fillna("").astype(str)

    out["theme_hint"] = get_series(out, "theme_hint", "other").fillna("other").astype(str)
    out["video_id"] = ""
    out["video_title"] = ""
    out["channel_title"] = ""
    out["video_score"] = None
    out["video_comment_count"] = None
    out["video_view_count"] = None
    out["comment_order_mode"] = ""
    out["app_id"] = get_series(out, "app_id", "").fillna("").astype(str)
    out["app_title"] = get_series(out, "app_title", "").fillna("").astype(str)
    out["review_created_version"] = get_series(out, "review_created_version", "").fillna("").astype(str)
    out["reply_content"] = get_series(out, "reply_content", "").fillna("").astype(str)
    out["replied_at"] = get_series(out, "replied_at", "").fillna("").astype(str)

    return out


def select_master_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["normalized_text"] = normalize_text_series(df["text"])

    master_cols = [
        "platform",
        "brand",
        "record_id",
        "parent_id",
        "text",
        "normalized_text",
        "title",
        "author",
        "created_at",
        "likes",
        "reply_count",
        "rating",
        "relevance_score",
        "theme_hint",
        "source_type_master",
        "query_used",
        "video_id",
        "video_title",
        "channel_title",
        "video_score",
        "video_comment_count",
        "video_view_count",
        "comment_order_mode",
        "app_id",
        "app_title",
        "review_created_version",
        "reply_content",
        "replied_at",
        "source_file",
        "source_folder",
    ]
    for c in master_cols:
        if c not in df.columns:
            df[c] = ""
    return df[master_cols]


def run_merge(google_input: str, output_dir: str) -> None:
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    google_df = safe_read_csv(google_input)
    combined = select_master_columns(standardize_google(google_df))
    combined.to_csv(outdir / "master_dataset_before_dedupe.csv", index=False)

    rows_before = len(combined)

    combined = combined.sort_values(
        by=["platform", "relevance_score", "likes", "reply_count"],
        ascending=[True, False, False, False],
        na_position="last",
    ).reset_index(drop=True)

    dedup_id = combined.drop_duplicates(subset=["platform", "record_id"], keep="first").copy()
    dedup_final = dedup_id.drop_duplicates(subset=["platform", "normalized_text"], keep="first").copy()
    dedup_final = dedup_final.reset_index(drop=True)

    dedup_id.to_csv(outdir / "master_dataset_dedup_by_id.csv", index=False)
    dedup_final.to_csv(outdir / "master_sentiment_dataset.csv", index=False)
    dedup_final.to_json(outdir / "master_sentiment_dataset.json", orient="records", indent=2, force_ascii=False)

    by_platform = (
        dedup_final.groupby("platform", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    by_platform.to_csv(outdir / "summary_by_platform.csv", index=False)

    by_theme = (
        dedup_final.groupby(["platform", "theme_hint"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["platform", "count"], ascending=[True, False])
    )
    by_theme.to_csv(outdir / "summary_by_platform_theme.csv", index=False)

    google_only = dedup_final[dedup_final["platform"] == "google_play"].copy()
    if not google_only.empty:
        by_rating = (
            google_only.groupby("rating", dropna=False)
            .size()
            .reset_index(name="count")
            .sort_values("rating", ascending=True)
        )
        by_rating.to_csv(outdir / "summary_google_by_rating.csv", index=False)

    text_stats = pd.DataFrame({
        "metric": [
            "rows_before_dedupe",
            "rows_after_id_dedupe",
            "rows_after_final_dedupe",
            "google_play_rows_after_final",
            "unique_normalized_text_all",
            "avg_text_len_chars",
            "median_text_len_chars",
            "avg_word_count",
            "median_word_count",
        ],
        "value": [
            int(rows_before),
            int(len(dedup_id)),
            int(len(dedup_final)),
            int((dedup_final["platform"] == "google_play").sum()),
            int(dedup_final["normalized_text"].nunique()),
            float(dedup_final["text"].str.len().mean()),
            float(dedup_final["text"].str.len().median()),
            float(dedup_final["text"].str.split().str.len().mean()),
            float(dedup_final["text"].str.split().str.len().median()),
        ],
    })
    text_stats.to_csv(outdir / "summary_text_stats.csv", index=False)

    theme_term_map = {
        "pricing": [r"\bprice\b", r"\bpricing\b", r"\bexpensive\b", r"\boverpriced\b", r"\bcharges?\b", r"\bfee\b", r"\bplatform fee\b", r"\bpacking charge\b", r"\bdelivery fee\b", r"\bhidden charges\b"],
        "quality": [r"\bquality\b", r"\bfood quality\b", r"\bstale\b", r"\bcold food\b", r"\bbad quality\b", r"\brotten\b", r"\bunhygienic\b", r"\btasteless\b", r"\bwrong order\b", r"\bgalat order\b"],
        "refund": [r"\brefund\b", r"\brefund nhi\b", r"\brefund nahi\b", r"\bpaise wapas\b"],
        "delivery": [r"\bdelivery\b", r"\blate delivery\b", r"\blate aaya\b", r"\bder se\b"],
        "support": [r"\bsupport\b", r"\bcustomer care\b", r"\bhelpdesk\b"],
    }

    for subset_name, terms in theme_term_map.items():
        subset = dedup_final[dedup_final["normalized_text"].str.contains("|".join(terms), regex=True, na=False)].copy()
        subset.to_csv(outdir / f"subset_{subset_name}.csv", index=False)

    summary = {
        "google_input": google_input,
        "rows_before_dedupe": int(rows_before),
        "rows_after_id_dedupe": int(len(dedup_id)),
        "rows_after_final_dedupe": int(len(dedup_final)),
        "google_play_rows_after_final": int((dedup_final["platform"] == "google_play").sum()),
        "platform_counts": dedup_final["platform"].value_counts(dropna=False).to_dict(),
        "google_rating_counts": (
            dedup_final.loc[dedup_final["platform"] == "google_play", "rating"]
            .dropna()
            .astype(float)
            .astype(int)
            .value_counts(dropna=False)
            .sort_index()
            .to_dict()
        ),
        "theme_counts_all": dedup_final["theme_hint"].value_counts(dropna=False).to_dict(),
        "notes": [
            "This master sentiment dataset is built only from deduplicated Google Play reviews.",
            "The script keeps the legacy filename for compatibility, but YouTube comments are no longer merged here.",
        ],
    }

    with open(outdir / "master_merge_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Done.")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--google_input", default=DEFAULT_GOOGLE_INPUT)
    parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    run_merge(
        google_input=args.google_input,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
