import csv
import json
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


INPUT_PATH = Path("master_sentiment_dataset") / "master_sentiment_dataset.csv"
OUTPUT_DIR = Path("master_final_dataset")
OUTPUT_CSV = OUTPUT_DIR / "master_final_dataset.csv"
OUTPUT_JSON_DATA = OUTPUT_DIR / "master_final_dataset.json"
OUTPUT_JSON = OUTPUT_DIR / "master_final_dataset_summary.json"


ROMAN_HINDI_MARKERS = {
    "nahi", "nhi", "hai", "bahut", "bekar", "bakwas", "accha", "acha",
    "mera", "meri", "mujhe", "muje", "kar", "kr", "paisa", "paise",
    "wapas", "bapas", "galat", "der", "chor", "mehenga", "sasta"
}

POSITIVE_TERMS = {
    "good", "great", "excellent", "amazing", "awesome", "best", "love",
    "loved", "nice", "fast", "quick", "helpful", "reliable", "convenient",
    "smooth", "easy", "satisfied", "happy", "delicious", "accha", "acha",
    "badhiya", "mast", "trustworthy", "honest", "responsive", "transparent",
    "value for money", "worth it"
}

NEGATIVE_TERMS = {
    "bad", "worst", "poor", "fake", "fraud", "scam", "late", "delay",
    "delayed", "cancel", "cancelled", "wrong", "missing", "refund",
    "problem", "issue", "pathetic", "terrible", "expensive", "overpriced",
    "hidden charges", "non refundable", "no support", "stale", "cold",
    "bakwas", "bekar", "chor", "unfair", "misleading", "complaint",
    "rude", "damaged", "puncture", "not received", "no refund",
    "disappointed", "disappointing", "frustrating", "awful", "horrible",
    "useless", "cheat", "cheated", "exploit", "taking advantage",
    "extra charges", "inflated prices", "bad experience", "removed reviews",
    "hidden reviews", "price hike", "stolen", "steal", "thief"
}

NEGATIONS = {"not", "no", "never", "nahi", "nhi", "mat"}

THEME_RULES = [
    (
        "refund_cancellation",
        [
            r"\brefund\b", r"\brefunded\b", r"\brefund nahi\b", r"\brefund nhi\b",
            r"\bpaise wapas\b", r"\bmoney back\b", r"\bcancel\b",
            r"\bcancelled\b", r"\bcancellation\b", r"\bnon refundable\b"
        ],
    ),
    (
        "delivery",
        [
            r"\bdelivery\b", r"\blate delivery\b", r"\bdelay\b", r"\bdelayed\b",
            r"\bdriver\b", r"\brider\b", r"\bboy\b", r"\bdelivered\b",
            r"\bpickup\b", r"\bdistance\b"
        ],
    ),
    (
        "pricing_fees",
        [
            r"\bprice\b", r"\bpricing\b", r"\boverpriced\b", r"\bexpensive\b",
            r"\bplatform fee\b", r"\bdelivery fee\b", r"\bdelivery charge\b",
            r"\bpacking charge\b", r"\bcharges?\b", r"\bfee\b", r"\bfees\b",
            r"\bdiscount\b", r"\boffer\b", r"\bcoupon\b", r"\bmehenga\b", r"\bsasta\b"
        ],
    ),
    (
        "customer_support",
        [
            r"\bcustomer support\b", r"\bcustomer care\b", r"\bsupport\b",
            r"\bhelpdesk\b", r"\bhelp\b", r"\bagent\b", r"\bchat support\b",
            r"\bno support\b", r"\bresponse\b", r"\bresolution\b"
        ],
    ),
    (
        "trust_reviews",
        [
            r"\bfake\b", r"\bfraud\b", r"\bscam\b", r"\bmisleading\b",
            r"\bhidden reviews?\b", r"\bremoved reviews?\b", r"\bratings?\b",
            r"\breviews?\b", r"\btrust\b", r"\btransparency\b"
        ],
    ),
    (
        "order_issue",
        [
            r"\bwrong order\b", r"\bmissing item\b", r"\bdamaged\b",
            r"\bitem missing\b", r"\bincorrect order\b", r"\bgalat order\b"
        ],
    ),
    (
        "food_quality",
        [
            r"\bfood quality\b", r"\bquality\b", r"\bstale\b", r"\bcold food\b",
            r"\bcold\b", r"\bexpired\b", r"\brotten\b", r"\bunhygienic\b",
            r"\btasteless\b", r"\bbad food\b", r"\bspoiled\b"
        ],
    ),
    (
        "app_experience",
        [
            r"\bapp\b", r"\bbug\b", r"\bbugs\b", r"\bcrash\b", r"\bcrashes\b",
            r"\blogin\b", r"\bpayment\b", r"\bupi\b", r"\bwallet\b",
            r"\botp\b", r"\binterface\b", r"\buser friendly\b", r"\bux\b",
            r"\bupdate\b", r"\btracking\b"
        ],
    ),
    (
        "competitor_comparison",
        [
            r"\bswiggy\b", r"\bblinkit\b", r"\bzepto\b", r"\bvs\b",
            r"\bbetter than\b", r"\bworse than\b", r"\bcompared to\b"
        ],
    ),
]

THEME_FALLBACK_MAP = {
    "app_ux": "app_experience",
    "customer_support": "customer_support",
    "delivery": "delivery",
    "pricing_fees": "pricing_fees",
    "refund": "refund_cancellation",
    "trust_reviews": "trust_reviews",
    "order_issue": "order_issue",
    "food_quality": "food_quality",
    "competitor_comparison": "competitor_comparison",
    "customer_issue": "customer_support",
    "other": "other",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (text or "").lower())).strip()


def parse_num(value):
    try:
        return float(value)
    except Exception:
        return None


def parse_date(value: str):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S.%f%z"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def detect_language(text: str) -> str:
    if re.search(r"[\u0900-\u097F]", text or ""):
        return "hi_devanagari"
    tokens = set(normalize_text(text).split())
    marker_hits = len(tokens & ROMAN_HINDI_MARKERS)
    if marker_hits >= 2:
        return "hi_romanized_or_mixed"
    return "en_or_mixed"


def count_term_hits(text: str, terms) -> int:
    lower = (text or "").lower()
    return sum(1 for term in terms if term in lower)


def infer_sentiment_from_text(text: str):
    norm = normalize_text(text)
    pos = count_term_hits(norm, POSITIVE_TERMS)
    neg = count_term_hits(norm, NEGATIVE_TERMS)

    words = norm.split()
    for idx, word in enumerate(words[:-1]):
        if word in NEGATIONS:
            nxt = words[idx + 1]
            if nxt in POSITIVE_TERMS:
                neg += 1
            if nxt in NEGATIVE_TERMS:
                pos += 1

    if neg > pos:
        label = "negative"
    elif pos > neg:
        label = "positive"
    else:
        label = "neutral"

    confidence = min(0.9, 0.55 + abs(neg - pos) * 0.08)
    if label == "neutral":
        confidence = 0.55 if (pos or neg) else 0.5
    return label, round(confidence, 2), pos, neg


def infer_sentiment(row):
    platform = row["platform"]
    rating_num = parse_num(row.get("rating", ""))
    text_label, text_conf, pos_hits, neg_hits = infer_sentiment_from_text(row.get("text", ""))

    if platform != "google_play":
        raise ValueError(f"Unexpected non-Google row in Google-only pipeline: {platform!r}")

    if rating_num is None:
        source = "google_text_fallback_missing_rating"
        return text_label, text_conf, source, False, pos_hits, neg_hits

    rating_int = int(rating_num)
    if rating_int <= 2:
        label = "negative"
    elif rating_int == 3:
        label = "neutral"
    else:
        label = "positive"

    mismatch = (
        (label == "positive" and text_label == "negative")
        or (label == "negative" and text_label == "positive")
    )
    confidence = 0.9 if not mismatch else 0.7
    source = "google_rating_proxy"
    return label, confidence, source, mismatch, pos_hits, neg_hits


def infer_theme(row):
    text = row.get("text", "")
    norm = normalize_text(text)
    for theme, patterns in THEME_RULES:
        for pattern in patterns:
            if re.search(pattern, norm):
                return theme, "keyword_rules"

    fallback = THEME_FALLBACK_MAP.get((row.get("theme_hint") or "").strip(), "other")
    return fallback, "fallback_from_theme_hint"


def bool_to_str(value: bool) -> str:
    return "1" if value else "0"


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing input dataset: {INPUT_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    final_rows = []
    sentiment_counts = Counter()
    sentiment_source_counts = Counter()
    theme_counts = Counter()
    theme_source_counts = Counter()
    language_counts = Counter()
    platform_counts = Counter()
    recent_counts = Counter()
    mismatch_count = 0

    for row in rows:
        sentiment_label, sentiment_confidence, sentiment_source, rating_text_mismatch, pos_hits, neg_hits = infer_sentiment(row)
        theme_final, theme_source = infer_theme(row)
        dt = parse_date(row.get("created_at", ""))
        language_hint = detect_language(row.get("text", ""))
        platform = row.get("platform", "")
        rating_num = parse_num(row.get("rating", ""))

        if dt and dt.year >= 2024:
            recent_bucket = "2024_plus"
        elif dt:
            recent_bucket = "pre_2024"
        else:
            recent_bucket = "unknown"

        final_row = {
            "platform": platform,
            "brand": row.get("brand", "zomato"),
            "record_id": row.get("record_id", ""),
            "text": row.get("text", "").strip(),
            "normalized_text": row.get("normalized_text", "").strip(),
            "text_length_chars": str(len((row.get("text") or "").strip())),
            "word_count": str(len((row.get("text") or "").split())),
            "language_hint": language_hint,
            "created_at": row.get("created_at", ""),
            "year": str(dt.year) if dt else "",
            "recent_bucket": recent_bucket,
            "likes": row.get("likes", "0"),
            "reply_count": row.get("reply_count", "0"),
            "rating": "" if rating_num is None else str(int(rating_num)),
            "relevance_score": row.get("relevance_score", "0"),
            "sentiment_label": sentiment_label,
            "sentiment_confidence": f"{sentiment_confidence:.2f}",
            "sentiment_label_source": sentiment_source,
            "rating_text_mismatch": bool_to_str(rating_text_mismatch),
            "positive_term_hits": str(pos_hits),
            "negative_term_hits": str(neg_hits),
            "theme_final": theme_final,
            "theme_label_source": theme_source,
            "platform_theme_original": row.get("theme_hint", ""),
            "source_type_master": row.get("source_type_master", ""),
            "query_used": row.get("query_used", ""),
            "title": row.get("title", ""),
            "author": row.get("author", ""),
            "video_id": row.get("video_id", ""),
            "video_title": row.get("video_title", ""),
            "channel_title": row.get("channel_title", ""),
            "video_score": row.get("video_score", ""),
            "video_comment_count": row.get("video_comment_count", ""),
            "video_view_count": row.get("video_view_count", ""),
            "comment_order_mode": row.get("comment_order_mode", ""),
            "app_id": row.get("app_id", ""),
            "app_title": row.get("app_title", ""),
            "source_folder": row.get("source_folder", ""),
            "label_ready_for_model": "1",
        }
        final_rows.append(final_row)

        sentiment_counts[sentiment_label] += 1
        sentiment_source_counts[sentiment_source] += 1
        theme_counts[theme_final] += 1
        theme_source_counts[theme_source] += 1
        language_counts[language_hint] += 1
        platform_counts[platform] += 1
        recent_counts[recent_bucket] += 1
        if rating_text_mismatch:
            mismatch_count += 1

    fieldnames = list(final_rows[0].keys()) if final_rows else []
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    with OUTPUT_JSON_DATA.open("w", encoding="utf-8") as f:
        json.dump(final_rows, f, indent=2, ensure_ascii=False)

    summary = {
        "input_file": str(INPUT_PATH),
        "output_file": str(OUTPUT_CSV),
        "output_json_file": str(OUTPUT_JSON_DATA),
        "rows": len(final_rows),
        "platform_counts": dict(platform_counts),
        "sentiment_counts": dict(sentiment_counts),
        "sentiment_label_source_counts": dict(sentiment_source_counts),
        "theme_final_counts": dict(theme_counts),
        "theme_label_source_counts": dict(theme_source_counts),
        "language_hint_counts": dict(language_counts),
        "recent_bucket_counts": dict(recent_counts),
        "rating_text_mismatch_google_only": mismatch_count,
        "notes": [
            "Google Play sentiment labels are derived from rating: 1-2 negative, 3 neutral, 4-5 positive.",
            "This final Zomato dataset is restricted to Google Play reviews only.",
            "Theme labels are standardized using keyword rules with fallback to original platform-specific theme hints."
        ],
    }

    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
