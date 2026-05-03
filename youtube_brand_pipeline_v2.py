import os
import re
import time
import math
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import requests
import pandas as pd
from dotenv import load_dotenv

# ---------------- Optional ML imports ----------------
USE_EMBEDDINGS = True
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except Exception:
    USE_EMBEDDINGS = False


# ---------------- Config ----------------
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
BRAND_NAME = os.getenv("BRAND_NAME", "zomato").strip().lower()
REGION_CODE = os.getenv("REGION_CODE", "IN").strip()
MAX_SEARCH_PAGES = int(os.getenv("MAX_SEARCH_PAGES", "3"))
SEARCH_RESULTS_PER_PAGE = min(int(os.getenv("SEARCH_RESULTS_PER_PAGE", "50")), 50)
TOP_VIDEOS_TO_HARVEST = int(os.getenv("TOP_VIDEOS_TO_HARVEST", "35"))
MAX_COMMENTS_PER_VIDEO = int(os.getenv("MAX_COMMENTS_PER_VIDEO", "300"))
MIN_VIDEO_COMMENT_COUNT = int(os.getenv("MIN_VIDEO_COMMENT_COUNT", "40"))
PUBLISHED_AFTER = os.getenv("PUBLISHED_AFTER", "2023-01-01T00:00:00Z")
FINAL_MAX_CLEANED_COMMENTS_PER_VIDEO = int(os.getenv("FINAL_MAX_CLEANED_COMMENTS_PER_VIDEO", "180"))

BASE_URL = "https://www.googleapis.com/youtube/v3"
OUTPUT_DIR = Path("output_v2")
RAW_DIR = OUTPUT_DIR / "raw"
CLEAN_DIR = OUTPUT_DIR / "cleaned"
RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

SEARCH_TOPIC = (
    f"Customer sentiment about {BRAND_NAME} brand strategy, customer trust, review transparency, "
    f"ratings, pricing, discounts, delivery charges, delivery experience, app experience, refunds, "
    f"customer support, service quality and comparison with competitors"
)

CANDIDATE_QUERIES = [
    f"{BRAND_NAME} review",
    f"{BRAND_NAME} customer review",
    f"{BRAND_NAME} complaint",
    f"{BRAND_NAME} customer support",
    f"{BRAND_NAME} refund issue",
    f"{BRAND_NAME} delivery charges",
    f"{BRAND_NAME} fake discount",
    f"{BRAND_NAME} discounts offers",
    f"{BRAND_NAME} misleading ratings",
    f"{BRAND_NAME} removed reviews",
    f"{BRAND_NAME} hidden reviews",
    f"{BRAND_NAME} review transparency",
    f"{BRAND_NAME} service experience",
    f"{BRAND_NAME} app problem",
    f"{BRAND_NAME} customer issue",
    f"{BRAND_NAME} ad campaign",
    f"{BRAND_NAME} platform fee",
    f"{BRAND_NAME} packing charges",
    f"{BRAND_NAME} price higher than restaurant",
    f"{BRAND_NAME} vs swiggy",
    f"swiggy vs {BRAND_NAME} review transparency",
    f"consumer complaint {BRAND_NAME}",
]

POSITIVE_HINTS = {
    BRAND_NAME: 10,
    "review": 6,
    "reviews": 6,
    "customer": 5,
    "customers": 5,
    "experience": 4,
    "complaint": 7,
    "complaints": 7,
    "support": 5,
    "refund": 7,
    "refunds": 7,
    "delivery": 4,
    "service": 4,
    "rating": 7,
    "ratings": 7,
    "hidden": 5,
    "removed": 5,
    "misleading": 6,
    "discount": 6,
    "discounts": 6,
    "offer": 4,
    "offers": 4,
    "charges": 5,
    "charge": 5,
    "price": 5,
    "pricing": 5,
    "app": 3,
    "campaign": 2,
    "transparency": 7,
    "trust": 6,
    "platform fee": 6,
    "packing charge": 6,
    "problem": 4,
    "issue": 4,
    "vs": 2,
    "swiggy": 2,
}

NEGATIVE_HINTS = {
    "meme": -10,
    "fight": -12,
    "slap": -12,
    "song": -8,
    "music": -8,
    "bgm": -8,
    "status": -8,
    "challenge": -10,
    "showdown": -10,
    "battle": -10,
    "salary": -12,
    "earnings": -12,
    "job": -12,
    "delivery boy": -12,
    "rider income": -12,
    "vlog": -6,
    "asmr": -10,
    "prank": -10,
    "funny": -5,
    "mukbang": -12,
    "recipe": -12,
    "food challenge": -12,
    "best rated food": -12,
    "worst rated food": -12,
    "game": -8,
    "gaming": -8,
    "pubg": -8,
    "free fire": -8,
}

# Hard reject only truly bad categories. Shorts are no longer hard-blocked.
VIDEO_BLOCK_PATTERNS = [
    r"\bfight\b",
    r"\bslap\b",
    r"\bsalary\b",
    r"\bearnings?\b",
    r"\bjob\b",
    r"\bdelivery boy\b",
    r"\brider income\b",
    r"\bmukbang\b",
    r"\brecipe\b",
    r"\bprank\b",
    r"\bfood challenge\b",
    r"\bbest rated food\b",
    r"\bworst rated food\b",
    r"\bpubg\b",
    r"\bfree fire\b",
]

COMMENT_RELEVANCE_TERMS = {
    BRAND_NAME,
    "review", "reviews", "rating", "ratings", "discount", "discounts", "offer", "offers",
    "delivery", "service", "support", "refund", "customer", "order", "orders",
    "price", "pricing", "charge", "charges", "app", "restaurant", "trust", "transparent",
    "transparency", "fake", "misleading", "hidden", "removed", "cancel", "cancelled",
    "issue", "problem", "experience", "delivery fee", "packing charge", "platform fee",
    "swiggy", "ondc"
}

CREATOR_META_PATTERNS = [
    r"\bpin me\b",
    r"\bpin this\b",
    r"\bthank(s| you)?\b",
    r"\bnice video\b",
    r"\bgreat video\b",
    r"\buseful video\b",
    r"\bkeep it up\b",
    r"\blove your videos\b",
    r"\bwho is here\b",
    r"\bfirst\b",
    r"\breply\b",
    r"\bheart this\b",
    r"\bpinned\b",
    r"\bsubscribed\b",
]

SHORT_GENERIC_COMMENTS = {
    "nice", "wow", "lol", "lmao", "bro", "good", "great", "super", "awesome",
    "fire", "cool", "op", "legend", "goat", "thanks", "thank you"
}

COMPETITOR_TERMS = {"ondc", "paytm", "swiggy", "rapido", "zepto", "blinkit"}
COMPARISON_TERMS = {"better than", "worse than", "compared to", "more than", "less than", "vs"}

SOURCE_TYPE_LABELS = [
    "customer_issue",
    "campaign_or_brand",
    "news_or_controversy",
    "competitor_comparison",
    "creator_tip_or_hack",
    "food_content_noise",
    "business_case_study",
    "other",
]


# ---------------- Utilities ----------------
def safe_request(url: str, params: Dict[str, Any], retries: int = 4, sleep_s: float = 1.0) -> Dict[str, Any]:
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=45)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(sleep_s * (attempt + 1))
    raise last_err


def youtube_get(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if not API_KEY:
        raise ValueError("YOUTUBE_API_KEY not found in .env")
    p = dict(params)
    p["key"] = API_KEY
    return safe_request(f"{BASE_URL}/{endpoint}", p)


def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def strip_urls(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", "", text or "").strip()


def compact_text(text: str) -> str:
    text = strip_urls(text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def contains_block_pattern(text: str) -> bool:
    t = normalize_text(text)
    return any(re.search(pat, t) for pat in VIDEO_BLOCK_PATTERNS)


def normalize_for_dedupe(text: str) -> str:
    t = normalize_text(strip_urls(text))
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def is_likely_emoji_or_symbol_only(text: str) -> bool:
    t = compact_text(text)
    if not t:
        return True
    alnum_count = sum(ch.isalnum() for ch in t)
    return alnum_count == 0


def is_very_short_comment(text: str) -> bool:
    t = compact_text(text)
    if len(t) < 5:
        return True
    words = t.split()
    return len(words) <= 2 and t.lower() in SHORT_GENERIC_COMMENTS


# ---------------- Search ----------------
def search_videos_paginated(query: str, max_pages: int = 3, per_page: int = 50) -> List[Dict[str, Any]]:
    results = []
    page_token = None

    for _ in range(max_pages):
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": per_page,
            "regionCode": REGION_CODE,
            "relevanceLanguage": "en",
            "order": "relevance",
            "publishedAfter": PUBLISHED_AFTER,
        }
        if page_token:
            params["pageToken"] = page_token

        data = youtube_get("search", params)

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue

            results.append({
                "search_query": query,
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

        time.sleep(0.15)

    return results


def get_video_stats(video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    stats_map = {}
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i + 50]
        data = youtube_get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch_ids),
            "maxResults": len(batch_ids),
        })

        for item in data.get("items", []):
            stats = item.get("statistics", {})
            sn = item.get("snippet", {})
            content = item.get("contentDetails", {})
            stats_map[item["id"]] = {
                "view_count": int(stats.get("viewCount", 0)) if stats.get("viewCount") else 0,
                "like_count": int(stats.get("likeCount", 0)) if stats.get("likeCount") else 0,
                "comment_count": int(stats.get("commentCount", 0)) if stats.get("commentCount") else 0,
                "tags": sn.get("tags", []),
                "category_id": sn.get("categoryId", ""),
                "duration": content.get("duration", ""),
            }
    return stats_map


# ---------------- Video type classification ----------------
def classify_source_type(row: Dict[str, Any]) -> str:
    text = normalize_text(
        " ".join([
            row.get("title", ""),
            row.get("description", ""),
            row.get("channel_title", ""),
            " ".join(row.get("tags", [])) if isinstance(row.get("tags"), list) else "",
        ])
    )

    if any(term in text for term in ["complaint", "refund", "support", "misleading", "ratings", "hidden reviews", "removed reviews", "delivery charges", "platform fee", "packing charge"]):
        return "customer_issue"

    if any(term in text for term in ["ad", "campaign", "brand film", "official", "marketing campaign"]):
        return "campaign_or_brand"

    if any(term in text for term in ["controversy", "asks customer", "language", "boycott", "viral issue", "news"]):
        return "news_or_controversy"

    if ("vs" in text or "comparison" in text or "better than" in text) and any(term in text for term in ["swiggy", "ondc", "paytm", "rapido"]):
        return "competitor_comparison"

    if any(term in text for term in ["how to get discount", "hack", "trick", "coupon", "save money"]):
        return "creator_tip_or_hack"

    if any(term in text for term in ["food challenge", "best food", "worst food", "mukbang", "recipe", "restaurant review of dish"]):
        return "food_content_noise"

    if any(term in text for term in ["marketing strategy", "case study", "business model", "how they revolutionized", "startup story"]):
        return "business_case_study"

    return "other"


def source_type_bonus(source_type: str) -> float:
    mapping = {
        "customer_issue": 10.0,
        "campaign_or_brand": 4.0,
        "competitor_comparison": 3.0,
        "news_or_controversy": 1.0,
        "business_case_study": -3.0,
        "creator_tip_or_hack": -5.0,
        "food_content_noise": -10.0,
        "other": 0.0,
    }
    return mapping.get(source_type, 0.0)


def passes_hard_video_filters(row: Dict[str, Any]) -> Tuple[bool, str]:
    text = normalize_text(
        " ".join([
            row.get("title", ""),
            row.get("description", ""),
            row.get("channel_title", ""),
            " ".join(row.get("tags", [])) if isinstance(row.get("tags"), list) else "",
        ])
    )

    if contains_block_pattern(text):
        return False, "blocked_pattern"

    if BRAND_NAME not in text and row.get("source_type") not in {"competitor_comparison"}:
        return False, "brand_missing"

    if row.get("comment_count", 0) < MIN_VIDEO_COMMENT_COUNT:
        return False, "low_comment_count"

    # keep Shorts only if very comment-rich and topic-relevant
    is_short = ("#shorts" in text) or (" shorts" in text) or ("shorts " in text)
    if is_short:
        strong_issue = any(term in text for term in [
            "discount", "rating", "review", "complaint", "refund",
            "support", "delivery charge", "platform fee", "packing charge"
        ])
        if not (row.get("comment_count", 0) >= 200 and strong_issue):
            return False, "shorts_not_strong_enough"

    if row.get("source_type") in {"food_content_noise"}:
        return False, "food_noise"

    return True, "ok"


# ---------------- Video ranking ----------------
def keyword_score(row: Dict[str, Any]) -> float:
    text = normalize_text(
        " ".join([
            row.get("title", ""),
            row.get("description", ""),
            row.get("channel_title", ""),
            " ".join(row.get("tags", [])) if isinstance(row.get("tags"), list) else "",
        ])
    )

    score = 0.0
    for kw, w in POSITIVE_HINTS.items():
        if kw in text:
            score += w
    for kw, w in NEGATIVE_HINTS.items():
        if kw in text:
            score += w

    cc = row.get("comment_count", 0)
    vc = row.get("view_count", 0)
    lc = row.get("like_count", 0)

    if cc > 0:
        score += min(10.0, math.log10(cc + 1) * 3.3)
    if vc > 0:
        score += min(3.0, math.log10(vc + 1) / 2.5)
    if lc > 0:
        score += min(2.0, math.log10(lc + 1) / 2.5)

    score += source_type_bonus(row.get("source_type", "other"))

    return score


def embedding_scores(rows: List[Dict[str, Any]], topic: str) -> List[float]:
    if not USE_EMBEDDINGS or not rows:
        return [0.0] * len(rows)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    docs = [
        " | ".join([
            r.get("title", ""),
            r.get("description", ""),
            r.get("channel_title", ""),
            " ".join(r.get("tags", [])) if isinstance(r.get("tags"), list) else "",
            r.get("source_type", ""),
        ])
        for r in rows
    ]

    emb_docs = model.encode(docs, normalize_embeddings=True, show_progress_bar=False)
    emb_topic = model.encode([topic], normalize_embeddings=True, show_progress_bar=False)[0]
    sims = np.dot(emb_docs, emb_topic)
    return sims.tolist()


def rank_videos(candidates: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not candidates:
        empty = pd.DataFrame()
        return empty, empty, empty

    dedup = {}
    for item in candidates:
        vid = item["video_id"]
        if vid not in dedup:
            dedup[vid] = item
        else:
            prev_q = dedup[vid].get("search_query", "")
            dedup[vid]["search_query"] = f"{prev_q} || {item.get('search_query', '')}"

    rows = list(dedup.values())
    stats_map = get_video_stats([r["video_id"] for r in rows])

    for r in rows:
        r.update(stats_map.get(r["video_id"], {}))
        r["source_type"] = classify_source_type(r)

    all_df = pd.DataFrame(rows)

    passed, filtered_out = [], []
    for r in rows:
        ok, reason = passes_hard_video_filters(r)
        r["hard_filter_result"] = reason
        if ok:
            passed.append(r)
        else:
            filtered_out.append(r)

    filtered_df = pd.DataFrame(filtered_out)

    if not passed:
        return all_df, filtered_df, pd.DataFrame()

    kw_scores = [keyword_score(r) for r in passed]
    emb_scores = embedding_scores(passed, SEARCH_TOPIC)

    for r, kw, em in zip(passed, kw_scores, emb_scores):
        r["keyword_score"] = round(float(kw), 4)
        r["embedding_score"] = round(float(em), 4)
        r["final_score"] = round(0.8 * float(kw) + 0.2 * float(em) * 10.0, 4)

    ranked_df = pd.DataFrame(passed).sort_values(
        by=["final_score", "comment_count", "view_count"],
        ascending=[False, False, False]
    )

    return all_df, filtered_df, ranked_df


# ---------------- Comment harvesting ----------------
def fetch_comments(video_id: str, max_comments: int = 300, order: str = "relevance") -> List[Dict[str, Any]]:
    comments = []
    page_token = None

    while len(comments) < max_comments:
        batch_size = min(100, max_comments - len(comments))
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": batch_size,
            "textFormat": "plainText",
            "order": order,
        }
        if page_token:
            params["pageToken"] = page_token

        data = youtube_get("commentThreads", params)

        for item in data.get("items", []):
            top = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            cid = item.get("snippet", {}).get("topLevelComment", {}).get("id", "")
            comments.append({
                "video_id": video_id,
                "comment_id": cid,
                "author": top.get("authorDisplayName", ""),
                "comment_text": top.get("textDisplay", ""),
                "like_count": int(top.get("likeCount", 0) or 0),
                "published_at": top.get("publishedAt", ""),
                "updated_at": top.get("updatedAt", ""),
                "reply_count": int(item.get("snippet", {}).get("totalReplyCount", 0) or 0),
                "comment_order_mode": order,
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

        time.sleep(0.12)

    return comments


# ---------------- Comment cleaning ----------------
def comment_keyword_relevance(text: str) -> int:
    t = normalize_text(text)
    score = 0
    for term in COMMENT_RELEVANCE_TERMS:
        if term in t:
            score += 1
    return score


def matches_meta_pattern(text: str) -> bool:
    t = normalize_text(text)
    return any(re.search(p, t) for p in CREATOR_META_PATTERNS)


def has_competitor_spillover_without_brand(text: str) -> bool:
    t = normalize_text(text)
    has_competitor = any(term in t for term in COMPETITOR_TERMS)
    has_brand = BRAND_NAME in t
    has_comparison = any(term in t for term in COMPARISON_TERMS)
    return has_competitor and (not has_brand) and (not has_comparison)


def is_comment_relevant(text: str) -> bool:
    t = compact_text(text)
    if not t:
        return False
    if is_likely_emoji_or_symbol_only(t):
        return False
    if is_very_short_comment(t):
        return False
    if matches_meta_pattern(t):
        return False
    if has_competitor_spillover_without_brand(t):
        return False

    rel = comment_keyword_relevance(t)
    if rel >= 1:
        return True

    # fallback: longer natural language comments
    if len(t.split()) >= 10:
        return True

    return False


def clean_comments_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    out = df.copy()
    out["comment_text"] = out["comment_text"].fillna("").map(compact_text)
    out["normalized_comment"] = out["comment_text"].map(normalize_for_dedupe)
    out["comment_relevance_score"] = out["comment_text"].map(comment_keyword_relevance)
    out["is_meta_comment"] = out["comment_text"].map(matches_meta_pattern)
    out["has_competitor_spillover_without_brand"] = out["comment_text"].map(has_competitor_spillover_without_brand)
    out["is_relevant_comment"] = out["comment_text"].map(is_comment_relevant)

    # basic filtering
    out = out[out["comment_text"].str.len() > 0]
    out = out[~out["comment_text"].map(is_likely_emoji_or_symbol_only)]
    out = out[~out["comment_text"].map(is_very_short_comment)]
    out = out[~out["is_meta_comment"]]
    out = out[~out["has_competitor_spillover_without_brand"]]

    # keep only relevant or clearly substantive
    out = out[(out["is_relevant_comment"]) | (out["comment_text"].str.split().str.len() >= 10)]

    # dedupe
    out = out.drop_duplicates(subset=["comment_id"], keep="first")
    out = out[out["normalized_comment"].str.len() > 0]
    out = out.drop_duplicates(subset=["video_id", "normalized_comment"], keep="first")

    # sort
    out = out.sort_values(
        by=["video_score", "comment_relevance_score", "like_count"],
        ascending=[False, False, False]
    )

    # cap per video so one viral source does not dominate
    out = (
        out.groupby("video_id", group_keys=False)
           .head(FINAL_MAX_CLEANED_COMMENTS_PER_VIDEO)
           .reset_index(drop=True)
    )

    return out


# ---------------- Main ----------------
def main():
    if not API_KEY:
        raise ValueError("Missing YOUTUBE_API_KEY in .env")

    print(f"Brand: {BRAND_NAME}")
    print(f"Region: {REGION_CODE}")
    print(f"Embeddings enabled: {USE_EMBEDDINGS}")
    print(f"Published after: {PUBLISHED_AFTER}")
    print(f"Queries: {len(CANDIDATE_QUERIES)}")

    all_candidates: List[Dict[str, Any]] = []

    # 1) Multi-page search
    for q in CANDIDATE_QUERIES:
        try:
            batch = search_videos_paginated(
                query=q,
                max_pages=MAX_SEARCH_PAGES,
                per_page=SEARCH_RESULTS_PER_PAGE
            )
            print(f"[search] {q} -> {len(batch)} videos")
            all_candidates.extend(batch)
            time.sleep(0.15)
        except Exception as e:
            print(f"[search-failed] {q}: {e}")

    raw_candidates_df = pd.DataFrame(all_candidates)
    raw_candidates_df.to_csv(RAW_DIR / "youtube_search_candidates_raw.csv", index=False)
    raw_candidates_df.to_json(RAW_DIR / "youtube_search_candidates_raw.json", orient="records", indent=2)

    # 2) Rank and filter
    all_videos_df, filtered_df, ranked_df = rank_videos(all_candidates)

    all_videos_df.to_csv(RAW_DIR / "youtube_all_videos_with_features_raw.csv", index=False)
    all_videos_df.to_json(RAW_DIR / "youtube_all_videos_with_features_raw.json", orient="records", indent=2)

    if not filtered_df.empty:
        filtered_df.to_csv(RAW_DIR / "youtube_filtered_out_videos_raw.csv", index=False)
        filtered_df.to_json(RAW_DIR / "youtube_filtered_out_videos_raw.json", orient="records", indent=2)

    if ranked_df.empty:
        print("No videos passed filters.")
        return

    ranked_df.to_csv(RAW_DIR / "youtube_ranked_videos_raw.csv", index=False)
    ranked_df.to_json(RAW_DIR / "youtube_ranked_videos_raw.json", orient="records", indent=2)

    shortlisted_df = ranked_df.head(TOP_VIDEOS_TO_HARVEST).copy()
    shortlisted_df.to_csv(CLEAN_DIR / "youtube_shortlisted_videos.csv", index=False)
    shortlisted_df.to_json(CLEAN_DIR / "youtube_shortlisted_videos.json", orient="records", indent=2)

    print(f"[rank] shortlisted videos: {len(shortlisted_df)}")

    # 3) Dual comment harvesting: relevance + time
    all_comments = []
    for _, row in shortlisted_df.iterrows():
        vid = row["video_id"]

        try:
            relevance_comments = fetch_comments(
                video_id=vid,
                max_comments=MAX_COMMENTS_PER_VIDEO,
                order="relevance",
            )
            time_comments = fetch_comments(
                video_id=vid,
                max_comments=MAX_COMMENTS_PER_VIDEO,
                order="time",
            )

            comments = relevance_comments + time_comments

            for c in comments:
                c["video_title"] = row.get("title", "")
                c["search_query"] = row.get("search_query", "")
                c["video_score"] = row.get("final_score", 0)
                c["video_comment_count"] = row.get("comment_count", 0)
                c["video_view_count"] = row.get("view_count", 0)
                c["channel_title"] = row.get("channel_title", "")
                c["source_type"] = row.get("source_type", "")
                c["hard_filter_result"] = row.get("hard_filter_result", "")

            all_comments.extend(comments)
            print(f"[comments] {vid} -> relevance={len(relevance_comments)}, time={len(time_comments)}")
            time.sleep(0.2)

        except Exception as e:
            print(f"[comments-failed] {vid}: {e}")

    comments_raw_df = pd.DataFrame(all_comments)
    comments_raw_df.to_csv(RAW_DIR / "youtube_comments_dataset_raw.csv", index=False)
    comments_raw_df.to_json(RAW_DIR / "youtube_comments_dataset_raw.json", orient="records", indent=2)

    # 4) Clean
    comments_clean_df = clean_comments_df(comments_raw_df)
    comments_clean_df.to_csv(CLEAN_DIR / "youtube_comments_dataset_cleaned.csv", index=False)
    comments_clean_df.to_json(CLEAN_DIR / "youtube_comments_dataset_cleaned.json", orient="records", indent=2)

    # 5) Summary
    source_type_counts = (
        shortlisted_df["source_type"].value_counts(dropna=False).to_dict()
        if "source_type" in shortlisted_df.columns else {}
    )

    summary = {
        "brand_name": BRAND_NAME,
        "region_code": REGION_CODE,
        "use_embeddings": USE_EMBEDDINGS,
        "published_after": PUBLISHED_AFTER,
        "num_queries": len(CANDIDATE_QUERIES),
        "raw_candidate_videos": int(len(raw_candidates_df)),
        "all_videos_with_features": int(len(all_videos_df)),
        "filtered_out_videos": int(len(filtered_df)),
        "ranked_videos": int(len(ranked_df)),
        "shortlisted_videos": int(len(shortlisted_df)),
        "raw_comments": int(len(comments_raw_df)),
        "cleaned_comments": int(len(comments_clean_df)),
        "source_type_counts_in_shortlist": source_type_counts,
        "output_dir": str(OUTPUT_DIR.resolve()),
    }

    with open(OUTPUT_DIR / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nDone.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()