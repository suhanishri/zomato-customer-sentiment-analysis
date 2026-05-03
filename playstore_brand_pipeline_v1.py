import os
import re
import time
import json
import argparse
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv

try:
    from google_play_scraper import app as gp_app
    from google_play_scraper import reviews as gp_reviews
    from google_play_scraper import Sort
except Exception as e:
    raise ImportError(
        "Please install google-play-scraper first: pip install google-play-scraper"
    ) from e


load_dotenv()

BRAND_NAME = os.getenv("BRAND_NAME", "zomato").strip().lower()

PLAYSTORE_APP_ID = os.getenv("PLAYSTORE_APP_ID", "com.application.zomato").strip()
PLAYSTORE_LANG = os.getenv("PLAYSTORE_LANG", "en").strip()
PLAYSTORE_COUNTRY = os.getenv("PLAYSTORE_COUNTRY", "in").strip()
PLAYSTORE_SLEEP_SECONDS = float(os.getenv("PLAYSTORE_SLEEP_SECONDS", "0.5"))
PLAYSTORE_BATCH_SIZE = int(os.getenv("PLAYSTORE_BATCH_SIZE", "200"))
PLAYSTORE_MAX_REVIEWS = int(os.getenv("PLAYSTORE_MAX_REVIEWS", "10000"))
PLAYSTORE_SORT = os.getenv("PLAYSTORE_SORT", "newest").strip().lower()

PLAYSTORE_MIN_TEXT_LEN = int(os.getenv("PLAYSTORE_MIN_TEXT_LEN", "8"))
PLAYSTORE_MIN_SCORE = int(os.getenv("PLAYSTORE_MIN_SCORE", "1"))

PLAYSTORE_OUTPUT_DIR = Path(os.getenv("PLAYSTORE_OUTPUT_DIR", "output_playstore"))
RAW = PLAYSTORE_OUTPUT_DIR / "raw"
CLEAN = PLAYSTORE_OUTPUT_DIR / "cleaned"
STATE = PLAYSTORE_OUTPUT_DIR / "state"
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)
STATE.mkdir(parents=True, exist_ok=True)

COMMENT_RELEVANCE_TERMS = {
    BRAND_NAME, "review", "reviews", "rating", "ratings", "discount", "discounts",
    "delivery", "late delivery", "support", "refund", "customer", "customer care",
    "order", "wrong order", "cancelled", "cancel", "price", "pricing", "charge", "charges",
    "app", "restaurant", "trust", "transparent", "transparency", "fake", "misleading",
    "hidden", "removed", "problem", "issue", "platform fee", "packing charge",
    "food quality", "bad experience", "scam", "swiggy"
}

COMMENT_RELEVANCE_TERMS_HI = {
    "mehenga", "mahinga", "late aaya", "der se", "refund nahi", "refund nhi",
    "paise wapas", "galat order", "bekar", "bakwas", "cancel kar diya", "support nahi", "fraud"
}

META_PATTERNS = [
    r"\bplz\b",
    r"\bplease fix\b",
    r"\bupdate app\b",
    r"\bworst app\b",
    r"\bgood app\b",
]

COMPETITOR_TERMS = {"ondc", "paytm", "swiggy", "rapido", "blinkit", "zepto", "ola food"}
COMPARISON_TERMS = {"better than", "worse than", "compared to", "vs", "more than", "less than"}


def save_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compact_text(text: str) -> str:
    text = re.sub(r"https?://\S+|www\.\S+", "", text or "")
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_for_dedupe(text: str) -> str:
    t = normalize_text(text)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def comment_keyword_relevance(text: str) -> int:
    t = normalize_text(text)
    score = sum(1 for term in COMMENT_RELEVANCE_TERMS if term in t)
    score += sum(1 for term in COMMENT_RELEVANCE_TERMS_HI if term in t)
    return score


def matches_meta_pattern(text: str) -> bool:
    t = normalize_text(text)
    return any(re.search(p, t) for p in META_PATTERNS)


def has_competitor_spillover_without_brand(text: str) -> bool:
    t = normalize_text(text)
    has_comp = any(term in t for term in COMPETITOR_TERMS)
    has_brand = BRAND_NAME in t
    has_comp_word = any(term in t for term in COMPARISON_TERMS)

    if has_comp and not has_brand and not has_comp_word:
        return True

    if any(term in t for term in ["zepto", "blinkit", "ola food"]) and BRAND_NAME not in t:
        return True

    return False


def is_relevant_text(text: str) -> bool:
    t = compact_text(text)
    nt = normalize_text(t)

    if not t:
        return False
    if len(t) < PLAYSTORE_MIN_TEXT_LEN:
        return False
    if matches_meta_pattern(t):
        return False
    if has_competitor_spillover_without_brand(t):
        return False

    rel = comment_keyword_relevance(t)
    has_brand = BRAND_NAME in nt

    if has_brand and rel >= 1:
        return True
    if rel >= 2:
        return True
    return False


def classify_text_theme(text: str) -> str:
    t = normalize_text(text)
    mapping = [
        ("refund", ["refund", "refund nahi", "refund nhi", "paise wapas"]),
        ("delivery", ["delivery", "late delivery", "late aaya", "der se"]),
        ("customer_support", ["support", "customer care", "helpdesk"]),
        ("pricing_fees", ["platform fee", "packing charge", "charges", "expensive", "mehenga", "pricing"]),
        ("order_issue", ["wrong order", "cancel", "cancelled", "galat order"]),
        ("trust_reviews", ["fake", "misleading", "hidden", "removed", "rating", "review", "trust"]),
        ("competitor_comparison", ["swiggy", "vs", "better than", "worse than"]),
        ("food_quality", ["food quality", "bad experience", "bekar", "bakwas"]),
        ("app_ux", ["app", "bug", "crash", "login", "payment", "update"]),
    ]
    for label, terms in mapping:
        if any(term in t for term in terms):
            return label
    return "other"


def parse_sort(sort_name: str):
    mapping = {
        "newest": Sort.NEWEST,
        "relevant": Sort.MOST_RELEVANT,
        "rating": Sort.RATING,
    }
    if sort_name not in mapping:
        raise ValueError("PLAYSTORE_SORT must be one of: newest, relevant, rating")
    return mapping[sort_name]


def get_app_metadata() -> Dict[str, Any]:
    return gp_app(
        PLAYSTORE_APP_ID,
        lang=PLAYSTORE_LANG,
        country=PLAYSTORE_COUNTRY,
    )


def review_row(review: Dict[str, Any], app_meta: Dict[str, Any]) -> Dict[str, Any]:
    review_id = review.get("reviewId") or normalize_for_dedupe(
        f"{review.get('userName','')}|{review.get('at','')}|{review.get('content','')[:80]}"
    )

    return {
        "platform": "google_play",
        "record_type": "review",
        "source_id": review_id,
        "parent_id": "",
        "app_id": PLAYSTORE_APP_ID,
        "app_title": app_meta.get("title", ""),
        "app_score": app_meta.get("score", ""),
        "app_installs": app_meta.get("installs", ""),
        "app_reviews_count": app_meta.get("reviews", ""),
        "search_query": PLAYSTORE_APP_ID,
        "title": app_meta.get("title", ""),
        "text": review.get("content", "") or "",
        "score": int(review.get("score", 0) or 0),
        "thumbs_up_count": int(review.get("thumbsUpCount", 0) or 0),
        "reply_count": 0,
        "author": review.get("userName", "") or "",
        "created_at": str(review.get("at", "") or ""),
        "review_created_version": review.get("reviewCreatedVersion", "") or "",
        "reply_content": review.get("replyContent", "") or "",
        "replied_at": str(review.get("repliedAt", "") or ""),
    }


def run_collect() -> None:
    """
    Important fix:
    We do NOT persist continuation_token in JSON state.
    The library returns a token object that is not safely JSON-roundtrippable.
    We keep collection simple and deterministic: each run starts from the beginning,
    dedupes by review ID, and stops when target count is reached.
    """
    state_path = STATE / "playstore_collect_state.json"

    rows = []
    seen_review_ids = set()

    if state_path.exists():
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            rows = state.get("rows", [])
            seen_review_ids = set(state.get("seen_review_ids", []))
        except Exception:
            rows = []
            seen_review_ids = set()

    app_meta = get_app_metadata()
    save_json(RAW / "playstore_app_metadata.json", app_meta)

    collected_this_run = 0
    sort_value = parse_sort(PLAYSTORE_SORT)

    continuation_token = None
    stagnant_batches = 0

    while len(seen_review_ids) < PLAYSTORE_MAX_REVIEWS:
        batch_reviews, continuation_token = gp_reviews(
            PLAYSTORE_APP_ID,
            lang=PLAYSTORE_LANG,
            country=PLAYSTORE_COUNTRY,
            sort=sort_value,
            count=min(PLAYSTORE_BATCH_SIZE, PLAYSTORE_MAX_REVIEWS),
            continuation_token=continuation_token,
        )

        if not batch_reviews:
            break

        new_in_batch = 0
        for review in batch_reviews:
            row = review_row(review, app_meta)
            if row["source_id"] in seen_review_ids:
                continue
            rows.append(row)
            seen_review_ids.add(row["source_id"])
            new_in_batch += 1
            collected_this_run += 1

            if len(seen_review_ids) >= PLAYSTORE_MAX_REVIEWS:
                break

        save_json(state_path, {
            "rows": rows,
            "seen_review_ids": sorted(seen_review_ids),
            "done": len(seen_review_ids) >= PLAYSTORE_MAX_REVIEWS or continuation_token is None,
        })

        print(f"[batch] fetched={len(batch_reviews)} new={new_in_batch} total={len(seen_review_ids)}")

        if new_in_batch == 0:
            stagnant_batches += 1
        else:
            stagnant_batches = 0

        if continuation_token is None:
            break

        if stagnant_batches >= 3:
            print("Stopping because batches are no longer adding new review IDs.")
            break

        time.sleep(PLAYSTORE_SLEEP_SECONDS)

    raw_df = pd.DataFrame(rows)
    raw_df.to_csv(RAW / "playstore_reviews_raw.csv", index=False)
    raw_df.to_json(RAW / "playstore_reviews_raw.json", orient="records", indent=2)

    summary = {
        "app_id": PLAYSTORE_APP_ID,
        "app_title": app_meta.get("title", ""),
        "raw_rows": int(len(raw_df)),
        "collected_this_run": int(collected_this_run),
        "done": len(seen_review_ids) >= PLAYSTORE_MAX_REVIEWS or continuation_token is None,
        "sort": PLAYSTORE_SORT,
        "lang": PLAYSTORE_LANG,
        "country": PLAYSTORE_COUNTRY,
    }
    save_json(PLAYSTORE_OUTPUT_DIR / "playstore_collect_summary.json", summary)
    print("Collection complete.")
    print(json.dumps(summary, indent=2))


def run_clean() -> None:
    raw_path = RAW / "playstore_reviews_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError("Run collect first. Missing raw/playstore_reviews_raw.csv")

    df = pd.read_csv(raw_path)
    if df.empty:
        df.to_csv(CLEAN / "playstore_reviews_cleaned.csv", index=False)
        save_json(PLAYSTORE_OUTPUT_DIR / "playstore_clean_summary.json", {"cleaned_rows": 0})
        print("No rows to clean.")
        return

    out = df.copy()
    out["text"] = out["text"].fillna("").map(compact_text)
    out["normalized_text"] = out["text"].map(normalize_for_dedupe)
    out["relevance_score"] = out["text"].map(comment_keyword_relevance)
    out["is_meta"] = out["text"].map(matches_meta_pattern)
    out["has_competitor_spillover_without_brand"] = out["text"].map(has_competitor_spillover_without_brand)
    out["is_relevant"] = out["text"].map(is_relevant_text)
    out["theme_hint"] = out["text"].map(classify_text_theme)

    out = out[out["text"].str.len() > 0]
    out = out[~out["is_meta"]]
    out = out[~out["has_competitor_spillover_without_brand"]]
    out = out[out["is_relevant"]]

    if "score" in out.columns:
        out = out[out["score"].fillna(0).astype(int) >= PLAYSTORE_MIN_SCORE]

    out = out[out["normalized_text"].str.len() > 0]
    out = out.drop_duplicates(subset=["platform", "record_type", "source_id"], keep="first")
    out = out.drop_duplicates(subset=["normalized_text"], keep="first")

    sort_cols = [c for c in ["relevance_score", "thumbs_up_count", "score"] if c in out.columns]
    out = out.sort_values(by=sort_cols, ascending=[False] * len(sort_cols)).reset_index(drop=True)

    out.to_csv(CLEAN / "playstore_reviews_cleaned.csv", index=False)
    out.to_json(CLEAN / "playstore_reviews_cleaned.json", orient="records", indent=2)

    summary = {
        "raw_rows": int(len(df)),
        "cleaned_rows": int(len(out)),
        "theme_counts": out["theme_hint"].value_counts(dropna=False).to_dict() if not out.empty else {},
        "rating_counts": out["score"].value_counts(dropna=False).sort_index().to_dict() if not out.empty else {},
    }
    save_json(PLAYSTORE_OUTPUT_DIR / "playstore_clean_summary.json", summary)
    print("Cleaning complete.")
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["collect", "clean"], required=True)
    args = parser.parse_args()

    if args.mode == "collect":
        run_collect()
    else:
        run_clean()


if __name__ == "__main__":
    main()
