import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List, Optional

def impute_missing_values(
    df: pd.DataFrame,
    numerical_strategy: str = "median",      # "median", "mean", "constant_zero", "drop"
    categorical_strategy: str = "mode",      # "mode", "constant_unknown", "drop"
    max_missing_threshold: float = 0.60,    # Threshold for flagging high missingness
    target_column: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Robust missing value imputation for numerical, categorical, string, and all-NaN columns:
    - Handles object columns with numeric strings by attempting numeric conversion where applicable
    - Handles completely empty (100% NaN) columns gracefully (falls back to 0 or 'Unknown')
    - Handles categorical mode calculation when all rows are null or no mode exists
    - Prevents silent alteration of target labels while reporting issues cleanly
    - Preserves dataframe index and structural integrity without exceptions
    """
    df = df.copy()
    imputation_log = []
    dropped_columns = []
    
    num_rows = len(df)
    
    for col in list(df.columns):
        if col == target_column:
            # Skip automatic silent imputation for target label
            missing_count = int(df[col].isnull().sum())
            if missing_count > 0:
                imputation_log.append({
                    "column": col,
                    "action": "flag_target_missing",
                    "missing_count": missing_count,
                    "note": "Target column has missing values. Recommended: drop rows with missing target."
                })
            continue

        missing_count = int(df[col].isnull().sum())
        if missing_count == 0:
            continue
            
        missing_rate = missing_count / max(num_rows, 1)
        
        # High missingness warning
        if missing_rate > max_missing_threshold:
            imputation_log.append({
                "column": col,
                "action": "high_missingness_detected",
                "missing_rate": round(missing_rate * 100, 1),
                "note": f"Column has > {int(max_missing_threshold*100)}% missing values."
            })

        # Try to infer if an object column is actually numeric
        is_numeric = np.issubdtype(df[col].dtype, np.number)
        if not is_numeric and df[col].dtype == object:
            # Check if converting to numeric succeeds for non-null values
            non_null_series = df[col].dropna()
            if not non_null_series.empty:
                numeric_converted = pd.to_numeric(non_null_series, errors="coerce")
                if numeric_converted.notnull().mean() > 0.8:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                    is_numeric = True
                    missing_count = int(df[col].isnull().sum())

        # Impute Numerical
        if is_numeric:
            fill_val = None
            valid_values = df[col].dropna()

            if valid_values.empty:
                # 100% missing numeric column
                fill_val = 0.0
            elif numerical_strategy == "mean":
                fill_val = valid_values.mean()
            elif numerical_strategy == "constant_zero":
                fill_val = 0.0
            else:  # default "median"
                fill_val = valid_values.median()

            # Fallback if median or mean is NaN (e.g. all NaNs)
            if fill_val is None or pd.isna(fill_val):
                fill_val = 0.0

            df[col] = df[col].fillna(fill_val)
            imputation_log.append({
                "column": col,
                "type": "numerical",
                "strategy": numerical_strategy,
                "fill_value": round(float(fill_val), 2),
                "imputed_count": missing_count
            })
                
        # Impute Categorical / Object / String
        else:
            fill_val = None
            valid_values = df[col].dropna()

            if valid_values.empty:
                # 100% missing categorical column
                fill_val = "Unknown"
            elif categorical_strategy == "mode":
                mode_series = valid_values.mode()
                fill_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"
            elif categorical_strategy == "constant_unknown":
                fill_val = "Unknown"
            else:
                mode_series = valid_values.mode()
                fill_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"

            if fill_val is None or pd.isna(fill_val):
                fill_val = "Unknown"

            # Fill with string fill_val safely
            df[col] = df[col].fillna(str(fill_val))
            imputation_log.append({
                "column": col,
                "type": "categorical",
                "strategy": categorical_strategy,
                "fill_value": str(fill_val),
                "imputed_count": missing_count
            })

    return df, {
        "operation": "impute_missing_values",
        "numerical_strategy": numerical_strategy,
        "categorical_strategy": categorical_strategy,
        "details": imputation_log,
        "dropped_columns": dropped_columns
    }
