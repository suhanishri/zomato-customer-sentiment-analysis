import os
import re
import time
import math
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

import requests
import pandas as pd
from dotenv import load_dotenv

USE_EMBEDDINGS = True
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except Exception:
    USE_EMBEDDINGS = False


load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
BRAND_NAME = os.getenv("BRAND_NAME", "zomato").strip().lower()
REGION_CODE = os.getenv("REGION_CODE", "IN").strip()
RELEVANCE_LANGUAGE = os.getenv("RELEVANCE_LANGUAGE", "en").strip()
MAX_SEARCH_PAGES = int(os.getenv("MAX_SEARCH_PAGES", "2"))
SEARCH_RESULTS_PER_PAGE = min(int(os.getenv("SEARCH_RESULTS_PER_PAGE", "25")), 50)
TOP_VIDEOS_TO_HARVEST = int(os.getenv("TOP_VIDEOS_TO_HARVEST", "20"))
MAX_COMMENTS_PER_VIDEO = int(os.getenv("MAX_COMMENTS_PER_VIDEO", "150"))
MIN_VIDEO_COMMENT_COUNT = int(os.getenv("MIN_VIDEO_COMMENT_COUNT", "25"))
PUBLISHED_AFTER = os.getenv("PUBLISHED_AFTER", "2023-01-01T00:00:00Z")
FINAL_MAX_CLEANED_COMMENTS_PER_VIDEO = int(os.getenv("FINAL_MAX_CLEANED_COMMENTS_PER_VIDEO", "100"))
ENABLE_EMBEDDINGS = os.getenv("ENABLE_EMBEDDINGS", "true").strip().lower() in {"1", "true", "yes", "y"}
FETCH_TIME_COMMENTS_FOR_TOP_N = int(os.getenv("FETCH_TIME_COMMENTS_FOR_TOP_N", "5"))
MIN_COMMENT_TEXT_LEN = int(os.getenv("MIN_COMMENT_TEXT_LEN", "8"))
STRICT_COMMENT_MATCH = os.getenv("STRICT_COMMENT_MATCH", "true").strip().lower() in {"1", "true", "yes", "y"}

BASE_URL = "https://www.googleapis.com/youtube/v3"
OUT = Path(os.getenv("OUTPUT_DIR", "output_v3"))
RAW = OUT / "raw"
CLEAN = OUT / "cleaned"
STATE = OUT / "state"
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)
STATE.mkdir(parents=True, exist_ok=True)

SEARCH_TOPIC = (
    f"Customer sentiment about {BRAND_NAME} brand strategy, customer trust, review transparency, "
    f"ratings, pricing, discounts, delivery charges, refunds, customer support, app problems, "
    f"service quality, delivery experience, platform fees, packing charges, food quality, wrong orders "
    f"and competitor comparisons"
)

CUSTOM_QUERIES = [q.strip() for q in os.getenv("CUSTOM_QUERIES", "").split("||") if q.strip()]

DEFAULT_CANDIDATE_QUERIES = [
    f"{BRAND_NAME} removed reviews",
    f"{BRAND_NAME} hidden reviews",
    f"{BRAND_NAME} misleading ratings",
    f"{BRAND_NAME} fake ratings",
    f"{BRAND_NAME} refund not received",
    f"{BRAND_NAME} order cancelled refund",
    f"{BRAND_NAME} refund issue",
    f"{BRAND_NAME} customer support issue",
    f"{BRAND_NAME} customer care issue",
    f"{BRAND_NAME} complaint",
    f"{BRAND_NAME} delivery charges complaint",
    f"{BRAND_NAME} platform fee complaint",
    f"{BRAND_NAME} packing charges complaint",
    f"{BRAND_NAME} food quality issue",
    f"{BRAND_NAME} wrong order refund",
    f"{BRAND_NAME} wrong order issue",
    f"{BRAND_NAME} late delivery complaint",
    f"{BRAND_NAME} late delivery refund",
    f"{BRAND_NAME} scam",
    f"{BRAND_NAME} review problem",
    f"{BRAND_NAME} charges too high",
    f"{BRAND_NAME} expensive after fees",
    f"{BRAND_NAME} trust issue",
    f"{BRAND_NAME} bad experience",
    f"{BRAND_NAME} vs swiggy reviews",
    f"{BRAND_NAME} review hindi",
    f"{BRAND_NAME} complaint hindi",
    f"{BRAND_NAME} refund nahi mila",
    f"{BRAND_NAME} delivery problem",
]

def unique_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
    return out

CANDIDATE_QUERIES = unique_preserve_order(CUSTOM_QUERIES if CUSTOM_QUERIES else DEFAULT_CANDIDATE_QUERIES)

POSITIVE_HINTS = {
    BRAND_NAME: 10,
    "customer": 5,
    "review": 6,
    "reviews": 6,
    "complaint": 7,
    "complaints": 7,
    "refund": 7,
    "support": 5,
    "customer care": 6,
    "rating": 7,
    "ratings": 7,
    "hidden": 5,
    "removed": 5,
    "misleading": 6,
    "discount": 6,
    "discounts": 6,
    "delivery charges": 6,
    "platform fee": 6,
    "packing charge": 6,
    "service": 4,
    "app": 3,
    "issue": 4,
    "problem": 4,
    "trust": 6,
    "transparency": 7,
    "late delivery": 6,
    "wrong order": 6,
    "food quality": 6,
    "vs": 2,
    "swiggy": 2,
}

NEGATIVE_HINTS = {
    "shorts": -3,
    "#shorts": -3,
    "delivery boy": -12,
    "rider": -10,
    "earning": -12,
    "earnings": -12,
    "job": -12,
    "tutorial": -8,
    "how to": -6,
    "guide": -6,
    "vlog": -6,
    "recipe": -12,
    "mukbang": -12,
    "best rated food": -12,
    "worst rated food": -12,
    "challenge": -10,
    "marketing strategy": -4,
    "business model": -4,
    "case study": -4,
    "startup story": -4,
}

BLOCK_PATTERNS = [
    r"\bdelivery boy\b",
    r"\brider\b",
    r"\bearnings?\b",
    r"\bjob\b",
    r"\btutorial\b",
    r"\bmukbang\b",
    r"\brecipe\b",
    r"\bfood challenge\b",
    r"\bbest rated food\b",
    r"\bworst rated food\b",
]

COMMENT_RELEVANCE_TERMS = {
    BRAND_NAME, "review", "reviews", "rating", "ratings", "discount", "discounts",
    "delivery", "late delivery", "support", "refund", "customer", "customer care",
    "order", "wrong order", "cancelled", "cancel", "price", "pricing",
    "charge", "charges", "app", "restaurant", "trust", "transparent", "transparency",
    "fake", "misleading", "hidden", "removed", "problem", "issue", "platform fee",
    "packing charge", "food quality", "bad experience", "scam", "swiggy"
}

COMMENT_RELEVANCE_TERMS_HI = {
    "mehenga", "mahinga", "late aaya", "der se", "refund nahi", "refund nhi",
    "paise wapas", "galat order", "bekar", "bakwas", "customer care", "delivery problem",
    "cancel kar diya", "support nahi", "fraud"
}

META_PATTERNS = [
    r"\bpin me\b", r"\bpin this\b", r"\bnice video\b", r"\bgreat video\b",
    r"\bthanks for sharing\b", r"\bkeep it up\b", r"\bwho is here\b",
    r"\bfirst\b", r"\breply\b", r"\bsubscribed\b", r"\bbig fan\b",
    r"\bvaluable information\b", r"\bhow to get fssai\b", r"\bfssai number\b",
    r"\bcustomer care ka number\b", r"\bemail kiska de\b", r"\bvideo banao\b",
]

COMPETITOR_TERMS = {"ondc", "paytm", "swiggy", "rapido", "blinkit", "zepto", "ola food"}
COMPARISON_TERMS = {"better than", "worse than", "compared to", "vs", "more than", "less than"}

NON_FATAL_COMMENT_REASONS = {
    "commentsDisabled",
    "videoNotFound",
    "forbidden",
    "disabledComments",
}


class YouTubeAPIError(Exception):
    def __init__(self, message: str, status_code: int = None, reason: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason


class QuotaOrAccessError(YouTubeAPIError):
    pass


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


def parse_youtube_error(resp: requests.Response):
    try:
        payload = resp.json()
        err = payload.get("error", {})
        errors = err.get("errors", [])
        reason = errors[0].get("reason") if errors else None
        message = err.get("message") or resp.text[:500]
        return reason or "unknown", message
    except Exception:
        return "unknown", resp.text[:500]


def request_json(url: str, params: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
    last_err = None
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=45)

            if r.status_code == 403:
                reason, message = parse_youtube_error(r)
                if reason in {"quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded", "userRateLimitExceeded"}:
                    raise QuotaOrAccessError(f"403 quota/access from YouTube API: {reason}: {message}", status_code=403, reason=reason)
                raise YouTubeAPIError(f"403 from YouTube API: {reason}: {message}", status_code=403, reason=reason)

            if r.status_code == 404:
                reason, message = parse_youtube_error(r)
                raise YouTubeAPIError(f"404 from YouTube API: {reason}: {message}", status_code=404, reason=reason)

            r.raise_for_status()
            return r.json()

        except QuotaOrAccessError:
            raise
        except YouTubeAPIError:
            raise
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (i + 1))

    raise last_err


def youtube_get(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if not API_KEY:
        raise ValueError("Missing YOUTUBE_API_KEY in .env")
    p = dict(params)
    p["key"] = API_KEY
    return request_json(f"{BASE_URL}/{endpoint}", p)


def search_videos_paginated(query: str, max_pages: int, per_page: int) -> List[Dict[str, Any]]:
    results = []
    page_token = None

    for _ in range(max_pages):
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": per_page,
            "regionCode": REGION_CODE,
            "relevanceLanguage": RELEVANCE_LANGUAGE,
            "order": "relevance",
            "publishedAfter": PUBLISHED_AFTER,
        }
        if page_token:
            params["pageToken"] = page_token

        data = youtube_get("search", params)

        for item in data.get("items", []):
            sn = item.get("snippet", {})
            vid = item.get("id", {}).get("videoId")
            if not vid:
                continue
            results.append({
                "search_query": query,
                "video_id": vid,
                "title": sn.get("title", ""),
                "description": sn.get("description", ""),
                "channel_title": sn.get("channelTitle", ""),
                "published_at": sn.get("publishedAt", ""),
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.15)

    return results


def get_video_stats(video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        data = youtube_get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "maxResults": len(batch),
        })
        for item in data.get("items", []):
            stats = item.get("statistics", {})
            sn = item.get("snippet", {})
            out[item["id"]] = {
                "view_count": int(stats.get("viewCount", 0) or 0),
                "like_count": int(stats.get("likeCount", 0) or 0),
                "comment_count": int(stats.get("commentCount", 0) or 0),
                "tags": sn.get("tags", []),
            }
    return out


def classify_source_type(row: Dict[str, Any]) -> str:
    text = normalize_text(" ".join([
        row.get("title", ""),
        row.get("description", ""),
        row.get("channel_title", ""),
        " ".join(row.get("tags", [])) if isinstance(row.get("tags"), list) else ""
    ]))

    if any(t in text for t in [
        "complaint", "refund", "support", "misleading", "ratings",
        "hidden reviews", "removed reviews", "delivery charges",
        "platform fee", "packing charge", "wrong order", "late delivery",
        "food quality", "order cancelled", "customer care", "bad experience", "scam"
    ]):
        return "customer_issue"

    if ("vs" in text or "comparison" in text or "better than" in text) and "swiggy" in text:
        return "competitor_comparison"

    if any(t in text for t in [
        "marketing strategy", "business model", "case study",
        "how they revolutionized", "startup story"
    ]):
        return "business_case_study"

    if any(t in text for t in [
        "discount code", "coupon", "save money", "hack", "trick", "how to get discount"
    ]):
        return "creator_tip_or_hack"

    if any(t in text for t in [
        "delivery boy", "rider", "salary", "earning", "job", "viral video"
    ]):
        return "food_or_partner_noise"

    return "other"


def source_type_bonus(source_type: str) -> float:
    return {
        "customer_issue": 12.0,
        "competitor_comparison": 3.0,
        "business_case_study": -6.0,
        "creator_tip_or_hack": -8.0,
        "food_or_partner_noise": -12.0,
        "other": 0.0,
    }.get(source_type, 0.0)


def passes_hard_video_filters(row: Dict[str, Any]):
    text = normalize_text(" ".join([
        row.get("title", ""),
        row.get("description", ""),
        row.get("channel_title", ""),
        " ".join(row.get("tags", [])) if isinstance(row.get("tags"), list) else ""
    ]))

    if any(re.search(p, text) for p in BLOCK_PATTERNS):
        return False, "blocked_pattern"

    if BRAND_NAME not in text and row.get("source_type") != "competitor_comparison":
        return False, "brand_missing"

    if row.get("comment_count", 0) < MIN_VIDEO_COMMENT_COUNT:
        return False, "low_comment_count"

    if row.get("source_type") in {"business_case_study", "creator_tip_or_hack", "food_or_partner_noise"}:
        return False, "low_quality_source_type"

    return True, "ok"


def keyword_score(row: Dict[str, Any]) -> float:
    text = normalize_text(" ".join([
        row.get("title", ""),
        row.get("description", ""),
        row.get("channel_title", ""),
        " ".join(row.get("tags", [])) if isinstance(row.get("tags"), list) else ""
    ]))
    score = 0.0
    for k, w in POSITIVE_HINTS.items():
        if k in text:
            score += w
    for k, w in NEGATIVE_HINTS.items():
        if k in text:
            score += w

    cc = row.get("comment_count", 0)
    vc = row.get("view_count", 0)
    lc = row.get("like_count", 0)

    if cc > 0:
        score += min(10.0, math.log10(cc + 1) * 3.0)
    if vc > 0:
        score += min(3.0, math.log10(vc + 1) / 2.5)
    if lc > 0:
        score += min(2.0, math.log10(lc + 1) / 2.5)

    score += source_type_bonus(row.get("source_type", "other"))
    return score


def embedding_scores(rows: List[Dict[str, Any]]) -> List[float]:
    if not (ENABLE_EMBEDDINGS and USE_EMBEDDINGS) or not rows:
        return [0.0] * len(rows)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    docs = [
        " | ".join([
            r.get("title", ""),
            r.get("description", ""),
            r.get("channel_title", ""),
            " ".join(r.get("tags", [])) if isinstance(r.get("tags"), list) else "",
            r.get("source_type", ""),
        ]) for r in rows
    ]
    emb_docs = model.encode(docs, normalize_embeddings=True, show_progress_bar=False)
    emb_topic = model.encode([SEARCH_TOPIC], normalize_embeddings=True, show_progress_bar=False)[0]
    sims = np.dot(emb_docs, emb_topic)
    return sims.tolist()


def run_discovery() -> None:
    search_state_path = STATE / "discovery_state.json"
    discovery_state = load_json(search_state_path, {
        "completed_queries": [],
        "candidate_rows": [],
        "stopped_on_quota_error": False,
    })

    completed = set(discovery_state["completed_queries"])
    all_candidates = discovery_state["candidate_rows"]

    try:
        for q in CANDIDATE_QUERIES:
            if q in completed:
                continue
            rows = search_videos_paginated(q, MAX_SEARCH_PAGES, SEARCH_RESULTS_PER_PAGE)
            all_candidates.extend(rows)
            completed.add(q)

            discovery_state = {
                "completed_queries": sorted(completed),
                "candidate_rows": all_candidates,
                "stopped_on_quota_error": False,
            }
            save_json(search_state_path, discovery_state)
            print(f"[search] {q} -> {len(rows)} videos")
            time.sleep(0.2)

    except QuotaOrAccessError as e:
        discovery_state = {
            "completed_queries": sorted(completed),
            "candidate_rows": all_candidates,
            "stopped_on_quota_error": True,
            "error": str(e),
        }
        save_json(search_state_path, discovery_state)
        print("Quota or access issue hit during discovery. Progress saved.")
        return

    raw_candidates_df = pd.DataFrame(all_candidates)
    raw_candidates_df.to_csv(RAW / "youtube_search_candidates_raw.csv", index=False)
    raw_candidates_df.to_json(RAW / "youtube_search_candidates_raw.json", orient="records", indent=2)

    dedup = {}
    for item in all_candidates:
        vid = item["video_id"]
        if vid not in dedup:
            dedup[vid] = item
        else:
            dedup[vid]["search_query"] = f'{dedup[vid]["search_query"]} || {item["search_query"]}'
    rows = list(dedup.values())

    stats_map = get_video_stats([r["video_id"] for r in rows]) if rows else {}
    for r in rows:
        r.update(stats_map.get(r["video_id"], {}))
        r["source_type"] = classify_source_type(r)
        ok, reason = passes_hard_video_filters(r)
        r["hard_filter_result"] = reason

    all_videos_df = pd.DataFrame(rows)
    all_videos_df.to_csv(RAW / "youtube_all_videos_with_features_raw.csv", index=False)
    all_videos_df.to_json(RAW / "youtube_all_videos_with_features_raw.json", orient="records", indent=2)

    filtered = [r for r in rows if r["hard_filter_result"] != "ok"]
    passed = [r for r in rows if r["hard_filter_result"] == "ok"]

    if filtered:
        filtered_df = pd.DataFrame(filtered)
        filtered_df.to_csv(RAW / "youtube_filtered_out_videos_raw.csv", index=False)
        filtered_df.to_json(RAW / "youtube_filtered_out_videos_raw.json", orient="records", indent=2)

    if not passed:
        print("No videos passed filters.")
        save_json(OUT / "discovery_summary.json", {
            "candidate_videos": int(len(raw_candidates_df)),
            "all_unique_videos": int(len(all_videos_df)),
            "ranked_videos": 0,
            "shortlisted_videos": 0,
            "completed_queries": sorted(completed),
        })
        return

    kw_scores = [keyword_score(r) for r in passed]
    emb_scores = embedding_scores(passed)

    for r, kw, em in zip(passed, kw_scores, emb_scores):
        r["keyword_score"] = round(float(kw), 4)
        r["embedding_score"] = round(float(em), 4)
        r["final_score"] = round(0.8 * float(kw) + 0.2 * float(em) * 10.0, 4)

    ranked_df = pd.DataFrame(passed).sort_values(
        by=["final_score", "comment_count", "view_count"],
        ascending=[False, False, False]
    )
    ranked_df.to_csv(RAW / "youtube_ranked_videos_raw.csv", index=False)
    ranked_df.to_json(RAW / "youtube_ranked_videos_raw.json", orient="records", indent=2)

    shortlist_df = ranked_df.head(TOP_VIDEOS_TO_HARVEST).copy()
    shortlist_df.to_csv(CLEAN / "youtube_shortlisted_videos.csv", index=False)
    shortlist_df.to_json(CLEAN / "youtube_shortlisted_videos.json", orient="records", indent=2)

    save_json(OUT / "discovery_summary.json", {
        "candidate_videos": int(len(raw_candidates_df)),
        "all_unique_videos": int(len(all_videos_df)),
        "filtered_out_videos": int(len(filtered)),
        "ranked_videos": int(len(ranked_df)),
        "shortlisted_videos": int(len(shortlist_df)),
        "completed_queries": sorted(completed),
    })
    print("Discovery complete.")


def fetch_comments(video_id: str, max_comments: int, order: str) -> List[Dict[str, Any]]:
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

        try:
            data = youtube_get("commentThreads", params)
        except YouTubeAPIError as e:
            if e.reason in NON_FATAL_COMMENT_REASONS:
                print(f"[comments-skipped] {video_id} -> {e.reason}")
                break
            raise

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


def comment_keyword_relevance(text: str) -> int:
    t = normalize_text(text)
    score = sum(1 for term in COMMENT_RELEVANCE_TERMS if term in t)
    score += sum(1 for term in COMMENT_RELEVANCE_TERMS_HI if term in t)
    return score


def is_relevant_comment(text: str) -> bool:
    t = compact_text(text)
    nt = normalize_text(t)

    if not t:
        return False
    if len(t) < MIN_COMMENT_TEXT_LEN:
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

    if not STRICT_COMMENT_MATCH and has_brand and len(t.split()) >= 12 and rel >= 0:
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
    out["is_relevant_comment"] = out["comment_text"].map(is_relevant_comment)

    out = out[out["comment_text"].str.len() > 0]
    out = out[~out["is_meta_comment"]]
    out = out[~out["has_competitor_spillover_without_brand"]]
    out = out[out["is_relevant_comment"]]
    out = out.drop_duplicates(subset=["comment_id"], keep="first")
    out = out[out["normalized_comment"].str.len() > 0]
    out = out.drop_duplicates(subset=["video_id", "normalized_comment"], keep="first")

    sort_cols = ["video_score", "comment_relevance_score", "like_count", "reply_count"]
    present_sort_cols = [c for c in sort_cols if c in out.columns]
    out = out.sort_values(
        by=present_sort_cols,
        ascending=[False] * len(present_sort_cols)
    )

    out = out.groupby("video_id", group_keys=False).head(FINAL_MAX_CLEANED_COMMENTS_PER_VIDEO).reset_index(drop=True)
    return out


def run_harvest() -> None:
    shortlist_path = CLEAN / "youtube_shortlisted_videos.csv"
    if not shortlist_path.exists():
        raise FileNotFoundError("Run discovery first. Missing cleaned/youtube_shortlisted_videos.csv")

    shortlist_df = pd.read_csv(shortlist_path)
    harvest_state_path = STATE / "harvest_state.json"
    harvest_state = load_json(harvest_state_path, {
        "done_video_ids": [],
        "rows": [],
        "stopped_on_quota_error": False,
    })

    done = set(harvest_state["done_video_ids"])
    all_rows = harvest_state["rows"]

    try:
        for idx, row in shortlist_df.iterrows():
            vid = row["video_id"]
            if vid in done:
                continue

            relevance_comments = fetch_comments(vid, MAX_COMMENTS_PER_VIDEO, "relevance")
            time_comments = fetch_comments(vid, MAX_COMMENTS_PER_VIDEO, "time") if idx < FETCH_TIME_COMMENTS_FOR_TOP_N else []
            comments = relevance_comments + time_comments

            for c in comments:
                c["video_title"] = row.get("title", "")
                c["search_query"] = row.get("search_query", "")
                c["video_score"] = row.get("final_score", 0)
                c["video_comment_count"] = row.get("comment_count", 0)
                c["video_view_count"] = row.get("view_count", 0)
                c["channel_title"] = row.get("channel_title", "")
                c["source_type"] = row.get("source_type", "")

            all_rows.extend(comments)
            done.add(vid)

            harvest_state = {
                "done_video_ids": sorted(done),
                "rows": all_rows,
                "stopped_on_quota_error": False,
            }
            save_json(harvest_state_path, harvest_state)
            print(f"[comments] {vid} -> relevance={len(relevance_comments)}, time={len(time_comments)}")
            time.sleep(0.2)

    except QuotaOrAccessError as e:
        harvest_state = {
            "done_video_ids": sorted(done),
            "rows": all_rows,
            "stopped_on_quota_error": True,
            "error": str(e),
        }
        save_json(harvest_state_path, harvest_state)
        print("Quota or access issue hit during harvest. Progress saved.")
    finally:
        raw_df = pd.DataFrame(all_rows)
        raw_df.to_csv(RAW / "youtube_comments_dataset_raw.csv", index=False)
        raw_df.to_json(RAW / "youtube_comments_dataset_raw.json", orient="records", indent=2)

        clean_df = clean_comments_df(raw_df)
        clean_df.to_csv(CLEAN / "youtube_comments_dataset_cleaned.csv", index=False)
        clean_df.to_json(CLEAN / "youtube_comments_dataset_cleaned.json", orient="records", indent=2)

        save_json(OUT / "harvest_summary.json", {
            "done_videos": len(done),
            "raw_comments": int(len(raw_df)),
            "cleaned_comments": int(len(clean_df)),
            "fetch_time_comments_for_top_n": FETCH_TIME_COMMENTS_FOR_TOP_N,
            "strict_comment_match": STRICT_COMMENT_MATCH,
        })
        print("Harvest pass saved.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["discover", "harvest"], required=True)
    args = parser.parse_args()

    if args.mode == "discover":
        run_discovery()
    else:
        run_harvest()


if __name__ == "__main__":
    main()
