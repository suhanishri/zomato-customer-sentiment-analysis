import os
import re
import time
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv

try:
    import praw
except Exception as e:
    raise ImportError("Please install praw first: pip install praw") from e


# ---------------- config ----------------
load_dotenv()

BRAND_NAME = os.getenv("BRAND_NAME", "zomato").strip().lower()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv(
    "REDDIT_USER_AGENT",
    f"{BRAND_NAME}_mba_sentiment_project by u/{REDDIT_USERNAME or 'your_username'}"
)

REDDIT_LIMIT_PER_QUERY = int(os.getenv("REDDIT_LIMIT_PER_QUERY", "250"))
REDDIT_COMMENT_LIMIT_PER_POST = int(os.getenv("REDDIT_COMMENT_LIMIT_PER_POST", "200"))
REDDIT_POST_SORT = os.getenv("REDDIT_POST_SORT", "relevance").strip().lower()
REDDIT_TIME_FILTER = os.getenv("REDDIT_TIME_FILTER", "all").strip().lower()
REDDIT_SLEEP_SECONDS = float(os.getenv("REDDIT_SLEEP_SECONDS", "0.8"))
REDDIT_MIN_COMMENT_SCORE = int(os.getenv("REDDIT_MIN_COMMENT_SCORE", "-5"))
REDDIT_MIN_TEXT_LEN = int(os.getenv("REDDIT_MIN_TEXT_LEN", "8"))
REDDIT_ENABLE_SUBMISSION_BODY = os.getenv("REDDIT_ENABLE_SUBMISSION_BODY", "true").strip().lower() in {"1", "true", "yes", "y"}

REDDIT_OUTPUT_DIR = Path(os.getenv("REDDIT_OUTPUT_DIR", "output_reddit"))
RAW = REDDIT_OUTPUT_DIR / "raw"
CLEAN = REDDIT_OUTPUT_DIR / "cleaned"
STATE = REDDIT_OUTPUT_DIR / "state"
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)
STATE.mkdir(parents=True, exist_ok=True)

DEFAULT_SUBREDDITS = [
    "india",
    "indiasocial",
    "bangalore",
    "delhi",
    "mumbai",
    "hyderabad",
    "pune",
    "chennai",
    "kolkata",
]

DEFAULT_QUERIES = [
    f"{BRAND_NAME}",
    f"{BRAND_NAME} review",
    f"{BRAND_NAME} complaint",
    f"{BRAND_NAME} refund",
    f"{BRAND_NAME} customer support",
    f"{BRAND_NAME} late delivery",
    f"{BRAND_NAME} wrong order",
    f"{BRAND_NAME} platform fee",
    f"{BRAND_NAME} packing charges",
    f"{BRAND_NAME} discount",
    f"{BRAND_NAME} scam",
    f"{BRAND_NAME} bad experience",
    f"{BRAND_NAME} vs swiggy",
    f"{BRAND_NAME} expensive",
]

CUSTOM_SUBREDDITS = [x.strip() for x in os.getenv("REDDIT_SUBREDDITS", "").split(",") if x.strip()]
CUSTOM_QUERIES = [x.strip() for x in os.getenv("REDDIT_SEARCH_QUERIES", "").split("||") if x.strip()]

SUBREDDITS = CUSTOM_SUBREDDITS if CUSTOM_SUBREDDITS else DEFAULT_SUBREDDITS
SEARCH_QUERIES = CUSTOM_QUERIES if CUSTOM_QUERIES else DEFAULT_QUERIES

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
    r"\bupvote\b",
    r"\bthis post\b",
    r"\bthanks for sharing\b",
    r"\bsource\?\b",
    r"\bop\b",
    r"\bremindme\b",
]

COMPETITOR_TERMS = {"ondc", "paytm", "swiggy", "rapido", "blinkit", "zepto", "ola food"}
COMPARISON_TERMS = {"better than", "worse than", "compared to", "vs", "more than", "less than"}


# ---------------- helpers ----------------
def save_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def unique_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
    return out


def ensure_credentials() -> None:
    required = {
        "REDDIT_CLIENT_ID": REDDIT_CLIENT_ID,
        "REDDIT_CLIENT_SECRET": REDDIT_CLIENT_SECRET,
        "REDDIT_USERNAME": REDDIT_USERNAME,
        "REDDIT_PASSWORD": REDDIT_PASSWORD,
        "REDDIT_USER_AGENT": REDDIT_USER_AGENT,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing Reddit credentials in .env: {', '.join(missing)}")


def build_reddit():
    ensure_credentials()
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
        check_for_async=False,
    )
    _ = reddit.user.me()
    return reddit


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
    if len(t) < REDDIT_MIN_TEXT_LEN:
        return False
    if matches_meta_pattern(t):
        return False
    if has_competitor_spillover_without_brand(t):
        return False

    rel = comment_keyword_relevance(t)
    has_brand = BRAND_NAME in nt

    if has_brand and rel >= 1:
        return True
    if rel >= 3:
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
    ]
    for label, terms in mapping:
        if any(term in t for term in terms):
            return label
    return "other"


def flatten_submission(submission, query: str) -> Dict[str, Any]:
    title = submission.title or ""
    selftext = submission.selftext or ""
    text = title
    if REDDIT_ENABLE_SUBMISSION_BODY and selftext:
        text = f"{title}\n\n{selftext}"

    return {
        "platform": "reddit",
        "record_type": "submission",
        "source_id": submission.id,
        "parent_id": "",
        "subreddit": str(submission.subreddit),
        "search_query": query,
        "title": title,
        "text": text,
        "score": int(getattr(submission, "score", 0) or 0),
        "reply_count": int(getattr(submission, "num_comments", 0) or 0),
        "author": str(submission.author) if submission.author else "",
        "created_utc": float(getattr(submission, "created_utc", 0.0) or 0.0),
        "url": f"https://www.reddit.com{submission.permalink}",
        "is_submission": True,
    }


def flatten_comment(comment, submission, query: str) -> Dict[str, Any]:
    return {
        "platform": "reddit",
        "record_type": "comment",
        "source_id": comment.id,
        "parent_id": getattr(comment, "parent_id", "") or "",
        "submission_id": submission.id,
        "submission_title": submission.title or "",
        "subreddit": str(submission.subreddit),
        "search_query": query,
        "title": submission.title or "",
        "text": comment.body or "",
        "score": int(getattr(comment, "score", 0) or 0),
        "reply_count": 0,
        "author": str(comment.author) if comment.author else "",
        "created_utc": float(getattr(comment, "created_utc", 0.0) or 0.0),
        "url": f"https://www.reddit.com{comment.permalink}",
        "is_submission": False,
    }


# ---------------- collection ----------------
def run_collect() -> None:
    reddit = build_reddit()

    state_path = STATE / "reddit_collect_state.json"
    state = load_json(state_path, {
        "completed_pairs": [],
        "rows": [],
        "seen_submission_ids": [],
        "seen_comment_ids": [],
    })

    completed_pairs = set(state["completed_pairs"])
    rows = state["rows"]
    seen_submission_ids = set(state["seen_submission_ids"])
    seen_comment_ids = set(state["seen_comment_ids"])

    subreddits = unique_preserve_order(SUBREDDITS)
    queries = unique_preserve_order(SEARCH_QUERIES)

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)

        for query in queries:
            pair_key = f"{subreddit_name}||{query}"
            if pair_key in completed_pairs:
                continue

            print(f"[search] r/{subreddit_name} | {query}")
            try:
                submissions = subreddit.search(
                    query=query,
                    sort=REDDIT_POST_SORT,
                    time_filter=REDDIT_TIME_FILTER,
                    limit=REDDIT_LIMIT_PER_QUERY,
                )

                count_added = 0
                for submission in submissions:
                    if submission.id not in seen_submission_ids:
                        row = flatten_submission(submission, query)
                        rows.append(row)
                        seen_submission_ids.add(submission.id)
                        count_added += 1

                    try:
                        submission.comments.replace_more(limit=0)
                        harvested = 0
                        for comment in submission.comments.list():
                            if harvested >= REDDIT_COMMENT_LIMIT_PER_POST:
                                break
                            if comment.id in seen_comment_ids:
                                continue
                            comment_row = flatten_comment(comment, submission, query)
                            rows.append(comment_row)
                            seen_comment_ids.add(comment.id)
                            harvested += 1
                    except Exception as e:
                        print(f"[comment-skip] {submission.id}: {e}")

                    time.sleep(REDDIT_SLEEP_SECONDS)

                completed_pairs.add(pair_key)
                save_json(state_path, {
                    "completed_pairs": sorted(completed_pairs),
                    "rows": rows,
                    "seen_submission_ids": sorted(seen_submission_ids),
                    "seen_comment_ids": sorted(seen_comment_ids),
                })
                print(f"[done] r/{subreddit_name} | {query} -> new submissions={count_added}")

            except Exception as e:
                save_json(state_path, {
                    "completed_pairs": sorted(completed_pairs),
                    "rows": rows,
                    "seen_submission_ids": sorted(seen_submission_ids),
                    "seen_comment_ids": sorted(seen_comment_ids),
                    "last_error": f"{subreddit_name} | {query} | {str(e)}",
                })
                print(f"[search-failed] r/{subreddit_name} | {query}: {e}")
                time.sleep(max(2.0, REDDIT_SLEEP_SECONDS))

    raw_df = pd.DataFrame(rows)
    raw_df.to_csv(RAW / "reddit_dataset_raw.csv", index=False)
    raw_df.to_json(RAW / "reddit_dataset_raw.json", orient="records", indent=2)

    summary = {
        "subreddits": subreddits,
        "queries": queries,
        "raw_rows": int(len(raw_df)),
        "unique_submissions": int(raw_df["source_id"].nunique()) if not raw_df.empty else 0,
    }
    save_json(REDDIT_OUTPUT_DIR / "reddit_collect_summary.json", summary)
    print("Collection complete.")
    print(json.dumps(summary, indent=2))


# ---------------- cleaning ----------------
def run_clean() -> None:
    raw_path = RAW / "reddit_dataset_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError("Run collect first. Missing raw/reddit_dataset_raw.csv")

    df = pd.read_csv(raw_path)
    if df.empty:
        df.to_csv(CLEAN / "reddit_dataset_cleaned.csv", index=False)
        save_json(REDDIT_OUTPUT_DIR / "reddit_clean_summary.json", {"cleaned_rows": 0})
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
        out = out[out["score"].fillna(0).astype(int) >= REDDIT_MIN_COMMENT_SCORE]

    out = out[out["normalized_text"].str.len() > 0]
    out = out.drop_duplicates(subset=["platform", "record_type", "source_id"], keep="first")
    out = out.drop_duplicates(subset=["subreddit", "normalized_text"], keep="first")

    sort_cols = [c for c in ["relevance_score", "score", "reply_count", "created_utc"] if c in out.columns]
    out = out.sort_values(by=sort_cols, ascending=[False] * len(sort_cols)).reset_index(drop=True)

    out.to_csv(CLEAN / "reddit_dataset_cleaned.csv", index=False)
    out.to_json(CLEAN / "reddit_dataset_cleaned.json", orient="records", indent=2)

    summary = {
        "raw_rows": int(len(df)),
        "cleaned_rows": int(len(out)),
        "unique_subreddits": int(out["subreddit"].nunique()) if not out.empty else 0,
        "record_type_counts": out["record_type"].value_counts(dropna=False).to_dict() if not out.empty else {},
        "theme_counts": out["theme_hint"].value_counts(dropna=False).to_dict() if not out.empty else {},
    }
    save_json(REDDIT_OUTPUT_DIR / "reddit_clean_summary.json", summary)
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
