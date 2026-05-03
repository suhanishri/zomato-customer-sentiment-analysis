from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

from modeling_utils import (
    INPUT_CSV,
    LABELS,
    MODEL_PRESETS,
    RESULTS_DIR,
    build_pipeline,
    ensure_dirs,
    get_modeling_df,
    load_dataset,
    save_json,
)

PAPER_REFERENCE = {
    "source": "Jonathan et al. (2019)",
    "comparison_kind": "paper_reported",
    "preset": "paper_reported_random_forest",
    "model_label": "Random Forest (paper-reported)",
    "paper_alignment": "Published paper result",
    "dataset_note": "Kaggle Bangalore restaurant reviews; different data source and label construction from our project.",
    "accuracy": 0.9244,
    "average_precision": 0.93,
    "average_recall": 0.87,
    "negative_precision": 0.93,
    "negative_recall": 0.89,
    "neutral_precision": 0.96,
    "neutral_recall": 0.73,
    "positive_precision": 0.92,
    "positive_recall": 0.99,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark multiple sentiment model presets on a shared split.")
    parser.add_argument(
        "--presets",
        nargs="*",
        default=list(MODEL_PRESETS.keys()),
        choices=sorted(MODEL_PRESETS.keys()),
        help="One or more preset names to benchmark.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()

    df = load_dataset()
    modeling_df = get_modeling_df(df)

    X_train, X_test, y_train, y_test = train_test_split(
        modeling_df["text"],
        modeling_df["sentiment_label"],
        test_size=0.2,
        random_state=42,
        stratify=modeling_df["sentiment_label"],
    )

    benchmark_rows: list[dict] = []
    detailed_reports: dict[str, dict] = {}
    confusion_matrices: dict[str, dict] = {}
    predictions_by_preset: dict[str, dict[str, object]] = {}

    for preset_name in args.presets:
        config = MODEL_PRESETS[preset_name]
        model = build_pipeline(preset_name)

        start = time.perf_counter()
        model.fit(X_train, y_train)
        train_seconds = round(time.perf_counter() - start, 2)

        predict_start = time.perf_counter()
        y_pred = model.predict(X_test)
        predict_seconds = round(time.perf_counter() - predict_start, 2)
        y_prob = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

        report = classification_report(y_test, y_pred, labels=LABELS, output_dict=True, zero_division=0)
        detailed_reports[preset_name] = report
        cm = confusion_matrix(y_test, y_pred, labels=LABELS)
        confusion_matrices[preset_name] = {
            "labels": LABELS,
            "matrix": cm.tolist(),
        }
        predictions_by_preset[preset_name] = {
            "predictions": y_pred,
            "probabilities": y_prob,
            "classes": list(model.named_steps["clf"].classes_) if hasattr(model.named_steps["clf"], "classes_") else [],
        }
        benchmark_rows.append(
            {
                "source": "our_recreated_benchmark",
                "comparison_kind": "holdout_eval",
                "preset": preset_name,
                "model_label": config["label"],
                "paper_alignment": config["paper_alignment"],
                "supports_proba": config["supports_proba"],
                "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
                "macro_precision": round(float(report["macro avg"]["precision"]), 4),
                "macro_recall": round(float(report["macro avg"]["recall"]), 4),
                "macro_f1": round(float(f1_score(y_test, y_pred, average="macro")), 4),
                "weighted_precision": round(float(report["weighted avg"]["precision"]), 4),
                "weighted_recall": round(float(report["weighted avg"]["recall"]), 4),
                "weighted_f1": round(float(f1_score(y_test, y_pred, average="weighted")), 4),
                "negative_precision": round(float(report["negative"]["precision"]), 4),
                "negative_recall": round(float(report["negative"]["recall"]), 4),
                "negative_f1": round(float(report["negative"]["f1-score"]), 4),
                "neutral_precision": round(float(report["neutral"]["precision"]), 4),
                "neutral_f1": round(float(report["neutral"]["f1-score"]), 4),
                "positive_precision": round(float(report["positive"]["precision"]), 4),
                "positive_recall": round(float(report["positive"]["recall"]), 4),
                "positive_f1": round(float(report["positive"]["f1-score"]), 4),
                "average_precision": round(float(report["macro avg"]["precision"]), 4),
                "average_recall": round(float(report["macro avg"]["recall"]), 4),
                "neutral_recall": round(float(report["neutral"]["recall"]), 4),
                "train_seconds": train_seconds,
                "predict_seconds": predict_seconds,
                "rows_train": int(len(X_train)),
                "rows_test": int(len(X_test)),
            }
        )

    benchmark_df = pd.DataFrame(benchmark_rows).sort_values(
        ["accuracy", "macro_f1", "neutral_f1"],
        ascending=[False, False, False],
    )
    benchmark_df.to_csv(RESULTS_DIR / "model_benchmark.csv", index=False)

    literature_rows = [PAPER_REFERENCE.copy()]

    if not benchmark_df.empty:
        best_row = benchmark_df.iloc[0].to_dict()
        best_row["dataset_note"] = "Our Google Play-only Zomato holdout evaluation."
        literature_rows.append(best_row)

    rf_rows = benchmark_df[benchmark_df["preset"] == "paper_style_random_forest"]
    if not rf_rows.empty:
        rf_row = rf_rows.iloc[0].to_dict()
        rf_row["dataset_note"] = "Our recreated Random Forest benchmark on the Google Play-only Zomato dataset."
        literature_rows.append(rf_row)

    literature_df = pd.DataFrame(literature_rows)
    literature_df.to_csv(RESULTS_DIR / "model_benchmark_literature.csv", index=False)

    if "tuned_word_lr" in predictions_by_preset and "paper_style_random_forest" in predictions_by_preset:
        best_bundle = predictions_by_preset["tuned_word_lr"]
        rf_bundle = predictions_by_preset["paper_style_random_forest"]
        comparison_df = modeling_df.loc[X_test.index, [
            "platform",
            "brand",
            "record_id",
            "text",
            "theme_final",
            "recent_bucket",
            "sentiment_label",
            "rating",
            "created_at",
        ]].copy()
        comparison_df["best_model_prediction"] = best_bundle["predictions"]
        comparison_df["random_forest_prediction"] = rf_bundle["predictions"]
        comparison_df["best_model_correct"] = comparison_df["best_model_prediction"] == comparison_df["sentiment_label"]
        comparison_df["random_forest_correct"] = comparison_df["random_forest_prediction"] == comparison_df["sentiment_label"]

        if best_bundle["probabilities"] is not None:
            best_classes = best_bundle["classes"]
            best_probs = best_bundle["probabilities"]
            comparison_df["best_model_confidence"] = [
                round(float(best_probs[i, best_classes.index(pred)]), 4)
                for i, pred in enumerate(comparison_df["best_model_prediction"])
            ]
        else:
            comparison_df["best_model_confidence"] = np.nan

        if rf_bundle["probabilities"] is not None:
            rf_classes = rf_bundle["classes"]
            rf_probs = rf_bundle["probabilities"]
            comparison_df["random_forest_confidence"] = [
                round(float(rf_probs[i, rf_classes.index(pred)]), 4)
                for i, pred in enumerate(comparison_df["random_forest_prediction"])
            ]
        else:
            comparison_df["random_forest_confidence"] = np.nan

        best_wins_df = comparison_df[
            comparison_df["best_model_correct"] & ~comparison_df["random_forest_correct"]
        ].copy()
        best_wins_df = best_wins_df.sort_values(
            ["best_model_confidence", "random_forest_confidence"],
            ascending=[False, False],
            na_position="last",
        )
        best_wins_df.to_csv(RESULTS_DIR / "benchmark_examples_best_vs_random_forest.csv", index=False)

        rf_wins_df = comparison_df[
            ~comparison_df["best_model_correct"] & comparison_df["random_forest_correct"]
        ].copy()
        rf_wins_df = rf_wins_df.sort_values(
            ["random_forest_confidence", "best_model_confidence"],
            ascending=[False, False],
            na_position="last",
        )
        rf_wins_df.to_csv(RESULTS_DIR / "benchmark_examples_random_forest_vs_best.csv", index=False)

    literature_summary = {
        "paper_reference": PAPER_REFERENCE,
        "best_model_on_our_data": benchmark_df.iloc[0].to_dict() if not benchmark_df.empty else {},
        "paper_style_random_forest_on_our_data": rf_rows.iloc[0].to_dict() if not rf_rows.empty else {},
        "example_files": {
            "best_model_beats_random_forest": str(RESULTS_DIR / "benchmark_examples_best_vs_random_forest.csv"),
            "random_forest_beats_best_model": str(RESULTS_DIR / "benchmark_examples_random_forest_vs_best.csv"),
        },
        "deltas_vs_paper": {},
        "comparison_note": (
            "Paper-reported scores and our recreated benchmarks are not directly equivalent because the datasets differ. "
            "The comparison is useful for methodological positioning, not for claiming a like-for-like reproduction."
        ),
    }

    if literature_summary["best_model_on_our_data"]:
        best = literature_summary["best_model_on_our_data"]
        literature_summary["deltas_vs_paper"]["best_model"] = {
            "accuracy_delta": round(float(best["accuracy"]) - PAPER_REFERENCE["accuracy"], 4),
            "average_precision_delta": round(float(best["average_precision"]) - PAPER_REFERENCE["average_precision"], 4),
            "average_recall_delta": round(float(best["average_recall"]) - PAPER_REFERENCE["average_recall"], 4),
            "negative_precision_delta": round(float(best["negative_precision"]) - PAPER_REFERENCE["negative_precision"], 4),
            "negative_recall_delta": round(float(best["negative_recall"]) - PAPER_REFERENCE["negative_recall"], 4),
            "neutral_precision_delta": round(float(best["neutral_precision"]) - PAPER_REFERENCE["neutral_precision"], 4),
            "neutral_recall_delta": round(float(best["neutral_recall"]) - PAPER_REFERENCE["neutral_recall"], 4),
            "positive_precision_delta": round(float(best["positive_precision"]) - PAPER_REFERENCE["positive_precision"], 4),
            "positive_recall_delta": round(float(best["positive_recall"]) - PAPER_REFERENCE["positive_recall"], 4),
        }
    if literature_summary["paper_style_random_forest_on_our_data"]:
        rf = literature_summary["paper_style_random_forest_on_our_data"]
        literature_summary["deltas_vs_paper"]["recreated_random_forest"] = {
            "accuracy_delta": round(float(rf["accuracy"]) - PAPER_REFERENCE["accuracy"], 4),
            "average_precision_delta": round(float(rf["average_precision"]) - PAPER_REFERENCE["average_precision"], 4),
            "average_recall_delta": round(float(rf["average_recall"]) - PAPER_REFERENCE["average_recall"], 4),
            "negative_precision_delta": round(float(rf["negative_precision"]) - PAPER_REFERENCE["negative_precision"], 4),
            "negative_recall_delta": round(float(rf["negative_recall"]) - PAPER_REFERENCE["negative_recall"], 4),
            "neutral_precision_delta": round(float(rf["neutral_precision"]) - PAPER_REFERENCE["neutral_precision"], 4),
            "neutral_recall_delta": round(float(rf["neutral_recall"]) - PAPER_REFERENCE["neutral_recall"], 4),
            "positive_precision_delta": round(float(rf["positive_precision"]) - PAPER_REFERENCE["positive_precision"], 4),
            "positive_recall_delta": round(float(rf["positive_recall"]) - PAPER_REFERENCE["positive_recall"], 4),
        }

    save_json(RESULTS_DIR / "model_benchmark_literature.json", literature_summary)
    save_json(RESULTS_DIR / "model_benchmark_reports.json", detailed_reports)
    save_json(RESULTS_DIR / "model_benchmark_confusion_matrices.json", confusion_matrices)

    summary = {
        "input_file": str(INPUT_CSV),
        "rows_modeling": int(len(modeling_df)),
        "benchmark_order": benchmark_df["preset"].tolist(),
        "best_by_accuracy": benchmark_df.iloc[0].to_dict() if not benchmark_df.empty else {},
        "benchmark_rows": benchmark_df.to_dict(orient="records"),
        "literature_file": str(RESULTS_DIR / "model_benchmark_literature.csv"),
    }
    save_json(RESULTS_DIR / "model_benchmark.json", summary)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
