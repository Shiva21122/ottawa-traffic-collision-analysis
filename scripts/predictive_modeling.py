"""
Ottawa Traffic Collision Analysis - Severity Prediction
Business Question: Can we predict whether a collision results in major/fatal injury
from time, location type, and road/light/weather conditions?
Model: Random Forest with GridSearchCV; evaluated with ROC-AUC and classification report.
Target: max_injury mapped to binary (Major/Fatal = 1, else 0).
Run from project root: python scripts/predictive_modeling.py
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    roc_curve,
)
import matplotlib.pyplot as plt

# 1) Load data
df = pd.read_csv("data/processed/Cleaned_Traffic_Data.csv").dropna(
    subset=["longitude", "latitude", "max_injury"]
)

# 2) Binary target
severity_map = {
    "00 - None":    0,
    "01 - Minimal": 0,
    "02 - Minor":   0,
    "03 - Major":   1,
    "04 - Fatal":   1,
}
df["y"] = df["max_injury"].map(severity_map)

# 3) Use existing date parts
df["dayofweek"] = df["day_of_week"]  # from CSV
df["month"]     = df["month"]
df["year"]      = df["year"]

# 4) Features
num_features = ["dayofweek", "month", "year"]
cat_features = ["light", "road_surface_condition", "environment_condition", "location_type"]

X = df[num_features + cat_features]
y = df["y"]

# 5) Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

# 6) Preprocessing pipeline
numeric_transformer = Pipeline([("scaler", StandardScaler())])
categorical_transformer = Pipeline([("onehot", OneHotEncoder(handle_unknown="ignore"))])
preprocessor = ColumnTransformer([
    ("num", numeric_transformer, num_features),
    ("cat", categorical_transformer, cat_features),
])

# 7) Model + tuning
pipe = Pipeline([("preproc", preprocessor), ("model", RandomForestClassifier())])
param_grid = {
    "model__n_estimators": [100, 200],
    "model__max_depth": [None, 10, 20],
}
grid = GridSearchCV(pipe, param_grid, cv=5, scoring="roc_auc", n_jobs=-1)
grid.fit(X_train, y_train)

# 8) Eval
best = grid.best_estimator_
y_pred = best.predict(X_test)
y_proba = best.predict_proba(X_test)[:,1]
print(classification_report(y_test, y_pred))
print("Test AUC:", roc_auc_score(y_test, y_proba))

# 9) ROC curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.plot(fpr, tpr, label=f"AUC={roc_auc_score(y_test,y_proba):.3f}")
plt.plot([0,1],[0,1],"--", color="grey")
plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate")
plt.legend(); plt.show()
