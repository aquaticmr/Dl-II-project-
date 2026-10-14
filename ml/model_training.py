import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)

def train_baseline_model(
    df: pd.DataFrame,
    target_column: str,
    model_type: str = "classification",  # "classification" or "regression"
    algorithm: str = "logistic_regression", # "logistic_regression", "decision_tree", "linear_regression"
    test_size: float = 0.25,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Trains a baseline model using a leakage-safe Scikit-Learn Pipeline.
    Imputation, encoding, and scaling are strictly fitted on the train split only!
    """
    if df is None or target_column not in df.columns:
        return {"error": f"Target column '{target_column}' not found in dataframe."}

    # Drop records where target is null
    df_clean = df.dropna(subset=[target_column]).copy()
    if len(df_clean) < 10:
        return {"error": "Insufficient observations (< 10 rows) after dropping missing target labels."}

    X = df_clean.drop(columns=[target_column])
    y = df_clean[target_column]

    # Drop obvious identifier columns (like Customer_ID, ID, etc.) that introduce noise
    id_like_cols = [c for c in X.columns if "id" in c.lower() or X[c].nunique() >= 0.95 * len(X)]
    if id_like_cols and len(X.columns) > len(id_like_cols):
        X = X.drop(columns=id_like_cols)

    num_features = list(X.select_dtypes(include=[np.number]).columns)
    cat_features = list(X.select_dtypes(include=["object", "string", "category"]).columns)

    if not num_features and not cat_features:
        return {"error": "No valid predictor features available for model training."}

    # Strict leakage-safe preprocessing pipelines
    transformers = []
    if num_features:
        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        transformers.append(("num", num_pipeline, num_features))

    if cat_features:
        cat_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        transformers.append(("cat", cat_pipeline, cat_features))

    preprocessor = ColumnTransformer(transformers=transformers)

    # Model selection
    if model_type == "classification":
        # Check target suitability
        if y.nunique() < 2:
            return {"error": "Classification target has fewer than 2 distinct classes."}

        stratify = y if y.value_counts().min() >= 2 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=stratify
        )

        if algorithm == "decision_tree":
            estimator = DecisionTreeClassifier(max_depth=5, random_state=random_state)
        else:
            estimator = LogisticRegression(max_iter=500, random_state=random_state)

        model_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", estimator)
        ])

        # Strictly fit on training set
        model_pipeline.fit(X_train, y_train)
        y_pred = model_pipeline.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()

        return {
            "status": "SUCCESS",
            "model_type": "classification",
            "algorithm": algorithm,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "metrics": {
                "accuracy": round(float(acc), 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1_score": round(float(f1), 4)
            },
            "confusion_matrix": cm,
            "classes": [str(c) for c in model_pipeline.classes_]
        }

    else: # Regression
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        if algorithm == "decision_tree":
            estimator = DecisionTreeRegressor(max_depth=5, random_state=random_state)
        else:
            estimator = LinearRegression()

        model_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", estimator)
        ])

        model_pipeline.fit(X_train, y_train)
        y_pred = model_pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        return {
            "status": "SUCCESS",
            "model_type": "regression",
            "algorithm": algorithm,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "metrics": {
                "mae": round(float(mae), 4),
                "rmse": round(float(rmse), 4),
                "r2_score": round(float(r2), 4)
            }
        }
