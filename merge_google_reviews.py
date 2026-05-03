import json
import argparse
from pathlib import Path
from typing import List

import pandas as pd


DEFAULT_INPUTS = [
    "output_playstore_newest_en/cleaned/playstore_reviews_cleaned.csv",
    "output_playstore_relevant_en/cleaned/playstore_reviews_cleaned.csv",
    "output_playstore_rating_en/cleaned/playstore_reviews_cleaned.csv",
    "output_playstore_newest_hi/cleaned/playstore_reviews_cleaned.csv",
]

DEFAULT_OUTPUT_DIR = "merged_google_reviews"


def normalize_text_series(s: pd.Series) -> pd.Series:
    return (
        s.fillna("")
         .astype(str)
         .str.lower()
         .str.replace(r"[^\w\s]", " ", regex=True)
         .str.replace(r"\s+", " ", regex=True)
         .str.strip()
    )


def load_one_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        print(f"[skip-missing] {p}")
        return pd.DataFrame()

    df = pd.read_csv(p)
    if df.empty:
        print(f"[skip-empty] {p}")
        return pd.DataFrame()

    df["source_file"] = str(p)
    df["source_folder"] = p.parts[0] if len(p.parts) > 0 else ""
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    required_defaults = {
        "platform": "google_play",
        "record_type": "review",
        "source_id": "",
        "text": "",
        "score": None,
        "thumbs_up_count": 0,
        "reply_count": 0,
        "author": "",
        "created_at": "",
        "theme_hint": "other",
        "relevance_score": 0,
        "app_id": "",
        "app_title": "",
        "search_query": "",
        "source_file": "",
        "source_folder": "",
    }

    for col, default in required_defaults.items():
        if col not in out.columns:
            out[col] = default

    out["text"] = out["text"].fillna("").astype(str).str.strip()
    out["normalized_text_merge"] = normalize_text_series(out["text"])

    numeric_cols = ["score", "thumbs_up_count", "reply_count", "relevance_score"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    keep_cols = [
        "platform",
        "record_type",
        "source_id",
        "text",
        "normalized_text_merge",
        "score",
        "thumbs_up_count",
        "reply_count",
        "author",
        "created_at",
        "theme_hint",
        "relevance_score",
        "app_id",
        "app_title",
        "search_query",
        "source_file",
        "source_folder",
    ]
    return out[keep_cols]


def merge_google_reviews(input_paths: List[str], output_dir: str) -> None:
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    parts = []
    for path in input_paths:
        df = load_one_csv(path)
        if not df.empty:
            parts.append(standardize_columns(df))

    if not parts:
        raise FileNotFoundError("No valid cleaned Play Store CSV files found.")

    combined = pd.concat(parts, ignore_index=True)

    combined.to_csv(outdir / "google_reviews_combined_before_dedupe.csv", index=False)

    before_rows = len(combined)
    before_unique_ids = combined["source_id"].nunique(dropna=True)
    before_unique_texts = combined["normalized_text_merge"].nunique(dropna=True)

    # Prefer rows with better analytical value
    combined = combined.sort_values(
        by=["relevance_score", "thumbs_up_count", "score"],
        ascending=[False, False, False],
        na_position="last",
    ).reset_index(drop=True)

    # Dedupe 1: exact review ID
    dedup_id = combined.drop_duplicates(subset=["source_id"], keep="first").copy()

    # Dedupe 2: fallback normalized text
    dedup_final = dedup_id.drop_duplicates(subset=["normalized_text_merge"], keep="first").copy()

    dedup_final = dedup_final.reset_index(drop=True)

    dedup_id.to_csv(outdir / "google_reviews_dedup_by_id.csv", index=False)
    dedup_final.to_csv(outdir / "google_reviews_master_cleaned.csv", index=False)
    dedup_final.to_json(outdir / "google_reviews_master_cleaned.json", orient="records", indent=2, force_ascii=False)

    summary = {
        "input_files": input_paths,
        "rows_before_dedupe": int(before_rows),
        "unique_source_ids_before": int(before_unique_ids),
        "unique_normalized_texts_before": int(before_unique_texts),
        "rows_after_id_dedupe": int(len(dedup_id)),
        "rows_after_final_dedupe": int(len(dedup_final)),
        "theme_counts": dedup_final["theme_hint"].value_counts(dropna=False).to_dict(),
        "rating_counts": (
            dedup_final["score"]
            .fillna(-999)
            .astype(int)
            .value_counts(dropna=False)
            .sort_index()
            .to_dict()
        ),
        "source_folder_counts": dedup_final["source_folder"].value_counts(dropna=False).to_dict(),
    }

    with open(outdir / "google_reviews_merge_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    theme_df = (
        dedup_final.groupby("theme_hint", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    theme_df.to_csv(outdir / "google_reviews_theme_counts.csv", index=False)

    rating_df = (
        dedup_final.groupby("score", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("score", ascending=True)
    )
    rating_df.to_csv(outdir / "google_reviews_rating_counts.csv", index=False)

    print("Done.")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputs",
        nargs="*",
        default=DEFAULT_INPUTS,
        help="List of cleaned Play Store CSV files to merge."
    )
    parser.add_argument(
        "--output_dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write merged review outputs into."
    )
    args = parser.parse_args()
    merge_google_reviews(args.inputs, args.output_dir)


if __name__ == "__main__":
    main()
