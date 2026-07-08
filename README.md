# Ottawa Traffic Collision Analysis (2017–2022)

End-to-end BI project: raw open data → Python cleaning pipeline → star-schema model → interactive Streamlit dashboard → Power BI report → machine-learning severity model.

## 1. Business Question

Where and when do severe traffic collisions occur in Ottawa, and which road, light, and weather conditions drive injury severity — so the city can prioritize safety interventions?

## 2. Research

- Source: City of Ottawa Open Data — traffic collision records 2017–2022 plus the 2019 collision-by-location file.
- Context: municipal road-safety programs (Vision Zero) target high-risk intersections and conditions; this analysis identifies them from historical data.

## 3. Data Types

Dates/times (parsed to datetime), categorical conditions (light, road surface, environment, traffic control), geographic coordinates (lat/long floats), injury classification (ordinal: None → Fatal).

## 4. Data Cleaning (`scripts/data_cleaning.py`)

- Standardized column names; parsed accident date and time
- Filled missing condition fields with "Unknown"; dropped columns >85% null
- Feature engineering: hour, day-of-week, month, year
- Modeled into a star schema: 1 fact table + 8 dimension tables (`data/processed/Dimtables.xlsx`)

## 5. Results

- **Streamlit dashboard** (`app.py`) with filters, Plotly visuals, logging, error handling, and CSV export
- **Power BI dashboard** (`dashboards/Ottawa_Traffic_Dashboard.pbix`) over the same star schema
- **Severity model** (`scripts/predictive_modeling.py`): Random Forest with GridSearchCV predicting major/fatal injury from time + conditions, evaluated with ROC-AUC and classification report
- Demo video in `media/`

## Project Structure

```
ottawa-traffic-collision-analysis/
├── app.py                      # Streamlit dashboard
├── requirements.txt
├── data/
│   ├── raw/                    # Original open-data extracts
│   └── processed/              # Cleaned fact table + dimension tables
├── scripts/
│   ├── data_cleaning.py        # Cleaning + feature engineering pipeline
│   ├── predictive_modeling.py  # Random Forest severity model
│   └── generate_geofiles.py    # GeoJSON/shape exports for mapping
├── dashboards/Ottawa_Traffic_Dashboard.pbix
├── docs/                       # Reference links
└── media/                      # Dashboard demo video (not pushed to GitHub)
```

## How to Run

```bash
pip install -r requirements.txt
python scripts/data_cleaning.py     # rebuild processed data
streamlit run app.py                # launch dashboard
python scripts/predictive_modeling.py
```

**Tools:** Python (pandas, scikit-learn, Plotly), Streamlit, Power BI, star-schema modeling
