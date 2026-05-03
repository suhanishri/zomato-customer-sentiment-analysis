# Zomato Dashboard Data

This folder contains dashboard-ready summary tables for the Zomato sentiment project.

## Purpose
These outputs are designed to be used as the data layer for a future Streamlit dashboard.

## Data source
- `../analysis_zomato_full/results/full_dataset_scored_predictions.csv`

## Main script
- `generate_dashboard_tables.py`

## Output folder
- `data/`

## Run command
```powershell
.venv\Scripts\python.exe dashboard_zomato\generate_dashboard_tables.py
```

## Intended dashboard sections
- Overview KPIs
- Sentiment distribution
- Theme-wise sentiment
- Year-wise trend
- Priority issues
- Example negative and positive comments
