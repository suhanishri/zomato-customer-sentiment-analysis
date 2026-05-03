# Zomato Full Sentiment Analysis

This folder contains the sentiment-analysis workflow for the Google Play-only Zomato final dataset.

## Input dataset
- `../master_final_dataset/master_final_dataset.csv`

## What this workflow does
- loads the Zomato final dataset
- expects the final dataset to contain only `google_play` rows
- creates a modeling subset for sentiment analysis
- trains configurable model presets such as `TF-IDF + Logistic Regression`
- evaluates the model on a stratified holdout set
- saves reports, confusion matrix, predictions, and model artifacts
- benchmarks multiple presets, including a Random Forest comparison aligned to the Jonathan et al. (2019) paper

## Main script
- `train_baseline_sentiment.py`
- `benchmark_models.py`

## Model presets
- `baseline_word_lr`
- `tuned_word_lr`
- `word_char_lr`
- `complement_nb`
- `calibrated_linear_svc`
- `paper_style_random_forest`

## Output folder
- `results/`

## Run command
```powershell
.venv\Scripts\python.exe analysis_zomato_full\train_baseline_sentiment.py
```

The default preset now trains the current best benchmark winner, `tuned_word_lr`, and saves it as `results/best_sentiment_pipeline.joblib`.

## Run a stronger preset
```powershell
.venv\Scripts\python.exe analysis_zomato_full\train_baseline_sentiment.py --preset word_char_lr --artifact-name best_sentiment_pipeline.joblib
```

## Run the benchmark suite
```powershell
.venv\Scripts\python.exe analysis_zomato_full\benchmark_models.py
```
