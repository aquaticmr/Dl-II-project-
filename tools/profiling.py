import pandas as pd
import numpy as np
from typing import Dict, Any, List

def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profiles a dataset and computes comprehensive summary metrics:
    - Dimensions, memory usage
    - Column data types categorized
    - Missing counts, percentages
    - Duplicate rows
    - Numerical column summary & IQR outliers
    - Categorical column cardinality & inconsistent capitalization flags
    - Near-constant or constant columns
    - Potential ID columns
    """
    if df is None or df.empty:
        return {
            "num_rows": 0,
            "num_columns": 0,
            "columns": [],
            "dtypes": {},
            "missing_values": {},
            "missing_pct": {},
            "total_missing": 0,
            "duplicate_rows": 0,
            "numerical_columns": [],
            "categorical_columns": [],
            "datetime_columns": [],
            "outliers": {},
            "constant_columns": [],
            "potential_id_columns": [],
            "quality_score": 0.0,
            "issues": ["Dataset is empty"]
        }

    num_rows, num_columns = df.shape
    columns = list(df.columns)
    
    # Classify columns
    num_cols = list(df.select_dtypes(include=[np.number]).columns)
    cat_cols = list(df.select_dtypes(include=["object", "category"]).columns)
    dt_cols = list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)
    
    # Missing values
    missing_counts = df.isnull().sum().to_dict()
    missing_pct = ((df.isnull().sum() / num_rows) * 100).round(2).to_dict()
    total_missing = int(df.isnull().sum().sum())
    
    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    
    # Constant and near-constant columns
    constant_columns = [col for col in columns if df[col].nunique(dropna=False) <= 1]
    
    # Potential ID columns (high cardinality, near 100% unique)
    potential_id_columns = [
        col for col in cat_cols + num_cols
        if df[col].nunique() >= 0.95 * num_rows and num_rows > 5
    ]
    
    # Numerical summaries and IQR outliers
    outliers = {}
    num_summary = {}
    for col in num_cols:
        series = df[col].dropna()
        if not series.empty:
            q25 = float(series.quantile(0.25))
            q75 = float(series.quantile(0.75))
            iqr = q75 - q25
            lower_bound = q25 - (1.5 * iqr)
            upper_bound = q75 + (1.5 * iqr)
            outlier_count = int(((series < lower_bound) | (series > upper_bound)).sum())
            outliers[col] = {
                "count": outlier_count,
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2)
            }
            num_summary[col] = {
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                "median": round(float(series.median()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2)
            }

    # Categorical inconsistencies (mixed casing, whitespace)
    inconsistent_categories = {}
    cat_summary = {}
    for col in cat_cols:
        series = df[col].dropna().astype(str)
        unique_vals = list(series.unique())
        cat_summary[col] = {
            "unique_count": len(unique_vals),
            "top_values": series.value_counts().head(5).to_dict()
        }
        # Check casing variants
        normalized_set = set(v.strip().lower() for v in unique_vals)
        if len(normalized_set) < len(unique_vals):
            inconsistent_categories[col] = {
                "unique_raw_count": len(unique_vals),
                "unique_normalized_count": len(normalized_set),
                "sample_variants": unique_vals[:6]
            }

    # Detected quality issues list
    issues = []
    if duplicate_rows > 0:
        issues.append(f"Found {duplicate_rows} duplicate rows.")
    if total_missing > 0:
        cols_with_missing = [c for c, count in missing_counts.items() if count > 0]
        issues.append(f"Missing values found in {len(cols_with_missing)} columns ({total_missing} cells total).")
    if inconsistent_categories:
        issues.append(f"Inconsistent categorical casing/whitespace in {len(inconsistent_categories)} columns: {list(inconsistent_categories.keys())}.")
    total_outliers = sum(o["count"] for o in outliers.values())
    if total_outliers > 0:
        issues.append(f"Detected {total_outliers} numerical outlier values across {len([c for c, o in outliers.items() if o['count'] > 0])} columns.")
    if constant_columns:
        issues.append(f"Constant/near-constant columns detected: {constant_columns}.")

    # Calculate Data Quality Score (0 - 100)
    # Weights: Completeness (40%), Uniqueness (25%), Consistency (20%), Outlier moderation (15%)
    total_cells = max(num_rows * num_columns, 1)
    completeness_score = max(0.0, 100.0 - ((total_missing / total_cells) * 100 * 2))
    uniqueness_score = max(0.0, 100.0 - ((duplicate_rows / max(num_rows, 1)) * 100 * 2))
    inconsistency_penalties = len(inconsistent_categories) * 10 + len(constant_columns) * 10
    consistency_score = max(0.0, 100.0 - inconsistency_penalties)
    outlier_cells = sum(o["count"] for o in outliers.values())
    outlier_score = max(0.0, 100.0 - ((outlier_cells / max(num_rows, 1)) * 15))
    
    quality_score = round(
        0.40 * completeness_score +
        0.25 * uniqueness_score +
        0.20 * consistency_score +
        0.15 * outlier_score, 
        1
    )

    return {
        "num_rows": num_rows,
        "num_columns": num_columns,
        "columns": columns,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": missing_counts,
        "missing_pct": missing_pct,
        "total_missing": total_missing,
        "duplicate_rows": duplicate_rows,
        "numerical_columns": num_cols,
        "categorical_columns": cat_cols,
        "datetime_columns": dt_cols,
        "num_summary": num_summary,
        "cat_summary": cat_summary,
        "outliers": outliers,
        "inconsistent_categories": inconsistent_categories,
        "constant_columns": constant_columns,
        "potential_id_columns": potential_id_columns,
        "quality_score": quality_score,
        "quality_components": {
            "completeness": round(completeness_score, 1),
            "uniqueness": round(uniqueness_score, 1),
            "consistency": round(consistency_score, 1),
            "outlier_health": round(outlier_score, 1)
        },
        "issues": issues
    }
