from __future__ import annotations

import argparse
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from modeling_utils import (
    INPUT_CSV,
    LABELS,
    MODEL_PRESETS,
    RESULTS_DIR,
    build_pipeline,
    ensure_dirs,
    get_feature_names,
    get_modeling_df,
    load_dataset,
    save_json,
)


def top_terms_by_class(model: Pipeline, top_n: int = 20) -> dict[str, dict[str, list[str]]]:
    clf = model.named_steps["clf"]
    feature_names_raw = get_feature_names(model)
    if feature_names_raw is None or not hasattr(clf, "coef_"):
        return {}

    feature_names = np.array(feature_names_raw)
    top_terms: dict[str, dict[str, list[str]]] = {}

    for idx, class_name in enumerate(clf.classes_):
        coefs = clf.coef_[idx]
        top_positive = feature_names[np.argsort(coefs)[-top_n:][::-1]].tolist()
        top_negative = feature_names[np.argsort(coefs)[:top_n]].tolist()
        top_terms[class_name] = {
            "top_positive_terms_for_class": top_positive,
            "top_negative_terms_for_class": top_negative,
        }
    return top_terms


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a sentiment model for the Zomato final dataset.")
    parser.add_argument(
        "--preset",
        default="tuned_word_lr",
        choices=sorted(MODEL_PRESETS.keys()),
        help="Model preset to train.",
    )
    parser.add_argument(
        "--artifact-name",
        default="best_sentiment_pipeline.joblib",
        help="Filename for the saved model artifact inside the results directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    df = load_dataset()
    modeling_df = get_modeling_df(df)

    dataset_summary = {
        "input_file": str(INPUT_CSV),
        "total_rows_input": int(len(df)),
        "total_rows_modeling": int(len(modeling_df)),
        "sentiment_counts": modeling_df["sentiment_label"].value_counts().to_dict(),
        "platform_counts": modeling_df["platform"].value_counts().to_dict(),
        "theme_counts": modeling_df["theme_final"].value_counts().head(15).to_dict(),
        "recent_bucket_counts": modeling_df["recent_bucket"].value_counts().to_dict(),
        "avg_text_len_chars": float(modeling_df["text"].str.len().mean()),
        "median_text_len_chars": float(modeling_df["text"].str.len().median()),
    }
    save_json(RESULTS_DIR / "dataset_summary.json", dataset_summary)

    X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(
        modeling_df["text"],
        modeling_df["sentiment_label"],
        modeling_df.index,
        test_size=0.2,
        random_state=42,
        stratify=modeling_df["sentiment_label"],
    )

    model = build_pipeline(args.preset)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

    metrics_summary = {
        "model_preset": args.preset,
        "model_label": MODEL_PRESETS[args.preset]["label"],
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "macro_f1": round(float(f1_score(y_test, y_pred, average="macro")), 4),
        "weighted_f1": round(float(f1_score(y_test, y_pred, average="weighted")), 4),
        "labels": LABELS,
    }
    save_json(RESULTS_DIR / "metrics_summary.json", metrics_summary)

    report = classification_report(y_test, y_pred, labels=LABELS, output_dict=True, zero_division=0)
    save_json(RESULTS_DIR / "classification_report.json", report)

    cm = confusion_matrix(y_test, y_pred, labels=LABELS)
    cm_df = pd.DataFrame(cm, index=[f"actual_{l}" for l in LABELS], columns=[f"pred_{l}" for l in LABELS])
    cm_df.to_csv(RESULTS_DIR / "confusion_matrix.csv", index=True)

    test_predictions = modeling_df.loc[test_idx, [
        "platform",
        "brand",
        "record_id",
        "text",
        "theme_final",
        "recent_bucket",
        "sentiment_label",
        "sentiment_label_source",
        "rating",
    ]].copy()
    test_predictions["predicted_sentiment"] = y_pred
    if y_prob is not None:
        prob_df = pd.DataFrame(y_prob, columns=[f"prob_{c}" for c in model.named_steps["clf"].classes_], index=test_predictions.index)
        test_predictions = pd.concat([test_predictions, prob_df], axis=1)
    test_predictions.to_csv(RESULTS_DIR / "test_predictions.csv", index=False)

    by_platform = []
    for platform_name, group in test_predictions.groupby("platform"):
        platform_acc = accuracy_score(group["sentiment_label"], group["predicted_sentiment"])
        platform_macro_f1 = f1_score(group["sentiment_label"], group["predicted_sentiment"], average="macro")
        by_platform.append(
            {
                "platform": platform_name,
                "rows": int(len(group)),
                "accuracy": round(float(platform_acc), 4),
                "macro_f1": round(float(platform_macro_f1), 4),
            }
        )
    pd.DataFrame(by_platform).to_csv(RESULTS_DIR / "metrics_by_platform.csv", index=False)

    feature_terms = top_terms_by_class(model, top_n=20)
    save_json(RESULTS_DIR / "top_terms_by_class.json", feature_terms)

    joblib.dump(model, RESULTS_DIR / args.artifact_name)

    print(json.dumps({
        "dataset_summary": dataset_summary,
        "metrics_summary": metrics_summary,
        "artifact_name": args.artifact_name,
        "results_dir": str(RESULTS_DIR),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
