# Analyzing Customer Sentiment Toward Zomato

Using Google Play Store reviews to study customer sentiment and derive implications for brand strategy and customer experience.

## Project overview

This repository contains the code, analysis workflow, dashboard assets, and presentation material for a Zomato-focused sentiment analysis project. The core work uses Google Play Store reviews to identify customer sentiment patterns, theme-level pain points, and actionable business insights.

While the broader workspace includes some comparative and supporting scripts, this repository is centered on the Zomato analysis pipeline.

## Research focus

- Understand how customers feel about Zomato through app review text
- Identify recurring experience themes such as delivery, refunds, app usability, and support
- Benchmark text classification models for sentiment prediction
- Translate review signals into brand strategy and customer experience insights

## Repository structure

```text
.
|-- analysis_zomato_full/          # Sentiment modeling, benchmarking, and results
|-- dashboard_app_zomato/          # Streamlit dashboard application
|-- dashboard_zomato/              # Dashboard-ready summary table generation
|-- documentation/                 # PPT/LaTeX documentation and presentation assets
|-- playstore_brand_pipeline_v1.py # Play Store review collection/processing pipeline
|-- build_master_final_dataset.py  # Final dataset construction helpers
|-- merge_google_youtube_master.py # Merge utilities for combined source datasets
`-- README.md
```

## Main workflow

### 1. Build or prepare the final dataset

The modeling workflow expects a final Zomato dataset with sentiment-ready fields. Some generator scripts are included in the repository, while large raw and intermediate datasets are intentionally excluded from version control.

### 2. Train the sentiment model

```powershell
.venv\Scripts\python.exe analysis_zomato_full\train_baseline_sentiment.py
```

By default, this trains the current best baseline preset and saves artifacts in `analysis_zomato_full/results/`.

### 3. Benchmark multiple model presets

```powershell
.venv\Scripts\python.exe analysis_zomato_full\benchmark_models.py
```

Available presets include TF-IDF based Logistic Regression, Complement Naive Bayes, calibrated Linear SVC, and a Random Forest comparison setup.

### 4. Generate dashboard tables

```powershell
.venv\Scripts\python.exe dashboard_zomato\generate_dashboard_tables.py
```

This produces dashboard-ready summary files under `dashboard_zomato/data/`.

### 5. Launch the Streamlit dashboard

```powershell
.venv\Scripts\python.exe -m streamlit run dashboard_app_zomato\app.py
```

## Key project components

### `analysis_zomato_full/`

- Model training and benchmarking scripts
- Shared modeling utilities
- Evaluation artifacts and scored outputs in `results/`

### `dashboard_zomato/`

- Generates structured summary tables for KPIs, sentiment trends, theme analysis, and example reviews

### `dashboard_app_zomato/`

- Interactive Streamlit interface for exploring Zomato sentiment insights

### `documentation/`

- Presentation deck and supporting documentation for the project deliverables

## Tech stack

- Python
- pandas
- scikit-learn
- Streamlit
- Plotly
- PptxGenJS

## Getting started

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install Python dependencies

Install the dependencies needed for the part of the project you want to run. For example:

```powershell
pip install -r dashboard_app_zomato\requirements.txt
```

Additional scripts may require packages from other requirement files in the repository.

### 3. Optional JavaScript dependency

If you need to regenerate presentation assets using the documentation scripts:

```powershell
npm install
```

## Outputs and insights

The repository supports:

- sentiment classification experiments on Zomato review data
- model benchmarking across multiple text pipelines
- dashboard generation for business-facing analysis
- presentation-ready documentation for academic or portfolio use

## Notes on data and version control

- Large datasets, exports, archives, and local environments are excluded through `.gitignore`
- `.env` and other sensitive local configuration files are not tracked
- If you clone this repository elsewhere, you may need to regenerate datasets before running the full pipeline end to end

## Project title

**Analyzing Customer Sentiment Toward Zomato Using Google Play Store Reviews: Implications for Brand Strategy and Customer Experience**
