from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
INPUT_CSV = PROJECT_DIR / "master_final_dataset" / "master_final_dataset.csv"
RESULTS_DIR = BASE_DIR / "results"
LABELS = ["negative", "neutral", "positive"]


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df["sentiment_label"] = df["sentiment_label"].fillna("").astype(str).str.strip()
    df["platform"] = df["platform"].fillna("").astype(str).str.strip()
    df["theme_final"] = df["theme_final"].fillna("other").astype(str).str.strip()
    df["recent_bucket"] = df["recent_bucket"].fillna("unknown").astype(str).str.strip()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["label_ready_for_model"] = df["label_ready_for_model"].fillna("0").astype(str).str.strip()
    platform_values = set(df["platform"].dropna().astype(str).str.strip().unique().tolist())
    unexpected_platforms = {value for value in platform_values if value and value != "google_play"}
    if unexpected_platforms:
        raise ValueError(
            f"Expected a Google Play-only final dataset, but found other platforms: {sorted(unexpected_platforms)}"
        )
    return df


def get_modeling_df(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        (df["label_ready_for_model"] == "1")
        & (df["text"].str.len() >= 8)
        & (df["sentiment_label"].isin(LABELS))
    ].copy()


def word_vectorizer(max_features: int = 30000, min_df: int = 3) -> TfidfVectorizer:
    return TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=min_df,
        max_df=0.95,
        max_features=max_features,
        sublinear_tf=True,
    )


def char_vectorizer(max_features: int = 20000) -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        lowercase=True,
        min_df=3,
        max_df=0.98,
        max_features=max_features,
        sublinear_tf=True,
    )


def build_pipeline(preset_name: str) -> Pipeline:
    if preset_name == "baseline_word_lr":
        clf = LogisticRegression(
            max_iter=1200,
            class_weight="balanced",
            random_state=42,
        )
        return Pipeline([("tfidf", word_vectorizer()), ("clf", clf)])

    if preset_name == "tuned_word_lr":
        clf = LogisticRegression(
            C=2.5,
            max_iter=1500,
            class_weight="balanced",
            random_state=42,
        )
        return Pipeline([("tfidf", word_vectorizer(max_features=40000, min_df=2)), ("clf", clf)])

    if preset_name == "word_char_lr":
        features = FeatureUnion(
            [
                ("word_tfidf", word_vectorizer(max_features=25000, min_df=2)),
                ("char_tfidf", char_vectorizer(max_features=20000)),
            ]
        )
        clf = LogisticRegression(
            C=2.0,
            max_iter=1500,
            class_weight="balanced",
            random_state=42,
        )
        return Pipeline([("features", features), ("clf", clf)])

    if preset_name == "complement_nb":
        clf = ComplementNB(alpha=0.7)
        return Pipeline([("tfidf", word_vectorizer(max_features=40000, min_df=2)), ("clf", clf)])

    if preset_name == "calibrated_linear_svc":
        features = FeatureUnion(
            [
                ("word_tfidf", word_vectorizer(max_features=25000, min_df=2)),
                ("char_tfidf", char_vectorizer(max_features=20000)),
            ]
        )
        base = LinearSVC(C=1.0, class_weight="balanced", random_state=42)
        clf = CalibratedClassifierCV(base, cv=3)
        return Pipeline([("features", features), ("clf", clf)])

    if preset_name == "paper_style_random_forest":
        clf = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
        )
        return Pipeline([("tfidf", word_vectorizer(max_features=8000, min_df=5)), ("clf", clf)])

    raise ValueError(f"Unknown preset: {preset_name}")


MODEL_PRESETS = {
    "baseline_word_lr": {
        "label": "Baseline TF-IDF + Logistic Regression",
        "supports_proba": True,
        "paper_alignment": "Current baseline",
    },
    "tuned_word_lr": {
        "label": "SentiLens",
        "supports_proba": True,
        "paper_alignment": "Improved linear baseline",
    },
    "word_char_lr": {
        "label": "Word + Char TF-IDF + Logistic Regression",
        "supports_proba": True,
        "paper_alignment": "Stronger text baseline",
    },
    "complement_nb": {
        "label": "TF-IDF + Complement Naive Bayes",
        "supports_proba": True,
        "paper_alignment": "Classical sparse-text baseline",
    },
    "calibrated_linear_svc": {
        "label": "Word + Char TF-IDF + Calibrated Linear SVC",
        "supports_proba": True,
        "paper_alignment": "High-accuracy linear margin model",
    },
    "paper_style_random_forest": {
        "label": "TF-IDF + Random Forest",
        "supports_proba": True,
        "paper_alignment": "Closest benchmark to Jonathan et al. (2019)",
    },
}


def get_feature_names(model: Pipeline) -> list[str] | None:
    for step_name in ("features", "tfidf"):
        if step_name not in model.named_steps:
            continue
        transformer = model.named_steps[step_name]
        if hasattr(transformer, "get_feature_names_out"):
            return transformer.get_feature_names_out().tolist()
    return None


def save_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
