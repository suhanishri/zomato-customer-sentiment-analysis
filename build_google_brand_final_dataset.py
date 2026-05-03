import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


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
            r"\bzomato\b", r"\bblinkit\b", r"\bzepto\b", r"\bvs\b",
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
    if len(tokens & ROMAN_HINDI_MARKERS) >= 2:
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
    return pos, neg


def infer_theme(text: str, original_theme: str):
    norm = normalize_text(text)
    for theme, patterns in THEME_RULES:
        for pattern in patterns:
            if re.search(pattern, norm):
                return theme, "keyword_rules"
    return THEME_FALLBACK_MAP.get((original_theme or "").strip(), "other"), "fallback_from_theme_hint"


def build_dataset(input_csv: Path, output_dir: Path, brand: str):
    with input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    output_dir.mkdir(parents=True, exist_ok=True)

    final_rows = []
    sentiment_counts = Counter()
    theme_counts = Counter()
    theme_source_counts = Counter()
    language_counts = Counter()
    recent_counts = Counter()
    mismatch_count = 0

    for row in rows:
        rating_num = parse_num(row.get("score", ""))
        rating_int = int(rating_num) if rating_num is not None else None

        if rating_int is None:
            sentiment_label = "neutral"
            sentiment_confidence = 0.5
            sentiment_source = "unknown"
        elif rating_int <= 2:
            sentiment_label = "negative"
            sentiment_confidence = 0.9
            sentiment_source = "google_rating_proxy"
        elif rating_int == 3:
            sentiment_label = "neutral"
            sentiment_confidence = 0.85
            sentiment_source = "google_rating_proxy"
        else:
            sentiment_label = "positive"
            sentiment_confidence = 0.9
            sentiment_source = "google_rating_proxy"

        pos_hits, neg_hits = infer_sentiment_from_text(row.get("text", ""))
        text_sentiment = "neutral"
        if neg_hits > pos_hits:
            text_sentiment = "negative"
        elif pos_hits > neg_hits:
            text_sentiment = "positive"

        rating_text_mismatch = (
            (sentiment_label == "positive" and text_sentiment == "negative")
            or (sentiment_label == "negative" and text_sentiment == "positive")
        )
        if rating_text_mismatch:
            sentiment_confidence = 0.7
            mismatch_count += 1

        theme_final, theme_source = infer_theme(row.get("text", ""), row.get("theme_hint", "other"))
        dt = parse_date(row.get("created_at", ""))
        language_hint = detect_language(row.get("text", ""))

        if dt and dt.year >= 2024:
            recent_bucket = "2024_plus"
        elif dt:
            recent_bucket = "pre_2024"
        else:
            recent_bucket = "unknown"

        final_row = {
            "platform": "google_play",
            "brand": brand,
            "record_id": row.get("source_id", ""),
            "text": (row.get("text") or "").strip(),
            "normalized_text": (row.get("normalized_text_merge") or normalize_text(row.get("text", ""))).strip(),
            "text_length_chars": str(len((row.get("text") or "").strip())),
            "word_count": str(len((row.get("text") or "").split())),
            "language_hint": language_hint,
            "created_at": row.get("created_at", ""),
            "year": str(dt.year) if dt else "",
            "recent_bucket": recent_bucket,
            "likes": row.get("thumbs_up_count", "0"),
            "reply_count": row.get("reply_count", "0"),
            "rating": "" if rating_int is None else str(rating_int),
            "relevance_score": row.get("relevance_score", "0"),
            "sentiment_label": sentiment_label,
            "sentiment_confidence": f"{sentiment_confidence:.2f}",
            "sentiment_label_source": sentiment_source,
            "rating_text_mismatch": "1" if rating_text_mismatch else "0",
            "positive_term_hits": str(pos_hits),
            "negative_term_hits": str(neg_hits),
            "theme_final": theme_final,
            "theme_label_source": theme_source,
            "platform_theme_original": row.get("theme_hint", ""),
            "source_type_master": row.get("theme_hint", ""),
            "query_used": row.get("search_query", ""),
            "title": "",
            "author": row.get("author", ""),
            "video_id": "",
            "video_title": "",
            "channel_title": "",
            "video_score": "",
            "video_comment_count": "",
            "video_view_count": "",
            "comment_order_mode": "",
            "app_id": row.get("app_id", ""),
            "app_title": row.get("app_title", ""),
            "source_folder": row.get("source_folder", ""),
            "label_ready_for_model": "1",
        }
        final_rows.append(final_row)

        sentiment_counts[sentiment_label] += 1
        theme_counts[theme_final] += 1
        theme_source_counts[theme_source] += 1
        language_counts[language_hint] += 1
        recent_counts[recent_bucket] += 1

    fieldnames = list(final_rows[0].keys()) if final_rows else []
    output_csv = output_dir / "master_final_dataset.csv"
    output_json = output_dir / "master_final_dataset.json"
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(final_rows, f, indent=2, ensure_ascii=False)

    summary = {
        "input_file": str(input_csv),
        "output_file": str(output_csv),
        "output_json_file": str(output_json),
        "brand": brand,
        "rows": len(final_rows),
        "sentiment_counts": dict(sentiment_counts),
        "theme_final_counts": dict(theme_counts),
        "theme_label_source_counts": dict(theme_source_counts),
        "language_hint_counts": dict(language_counts),
        "recent_bucket_counts": dict(recent_counts),
        "rating_text_mismatch_google_only": mismatch_count,
        "notes": [
            "Sentiment labels are derived from Google Play rating: 1-2 negative, 3 neutral, 4-5 positive.",
            "Theme labels are standardized with keyword rules and fallback to original platform theme hints.",
            "This file excludes YouTube by design."
        ],
    }
    with (output_dir / "master_final_dataset_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--brand", required=True)
    args = parser.parse_args()

    build_dataset(
        input_csv=Path(args.input_csv),
        output_dir=Path(args.output_dir),
        brand=args.brand.strip().lower(),
    )


if __name__ == "__main__":
    main()
